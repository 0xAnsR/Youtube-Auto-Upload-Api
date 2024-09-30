import argparse
from http import client
import httplib2
import os
import random
import time
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

# Explicitly tell the underlying HTTP transport library not to retry.
httplib2.RETRIES = 1
MAX_RETRIES = 10
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, client.NotConnected,
                        client.IncompleteRead, client.ImproperConnectionState,
                        client.CannotSendRequest, client.CannotSendHeader,
                        client.ResponseNotReady, client.BadStatusLine)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

CLIENT_SECRETS_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')
CREDS_FILE = 'token.json'  # File to save the user's credentials

def get_authenticated_service():
    credentials = None

    # Check if the credentials file exists
    if os.path.exists(CREDS_FILE):
        credentials = google.oauth2.credentials.Credentials.from_authorized_user_file(CREDS_FILE, SCOPES)

    # If there are no valid credentials, let the user log in
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(httplib2.Http())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=8080)

        # Save the credentials for the next run
        with open(CREDS_FILE, 'w') as token:
            token.write(credentials.to_json())

    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

def initialize_upload(youtube, options):
    tags = None
    if options.keywords:
        tags = options.keywords.split(',')

    body = dict(
        snippet=dict(
            title=options.title,
            description=options.description,
            tags=tags,
            categoryId=options.category
        ),
        status=dict(
            privacyStatus=options.privacyStatus
        )
    )

    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request)

def resumable_upload(request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print('Uploading file...')
            status, response = request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print('Video id "%s" was successfully uploaded.' % response['id'])
                else:
                    exit('The upload failed with an unexpected response: %s' % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = 'A retriable HTTP error %d occurred:\n%s' % (e.resp.status, e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = 'A retriable error occurred: %s' % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit('No longer attempting to retry.')

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print('Sleeping %f seconds and then retrying...' % sleep_seconds)
            time.sleep(sleep_seconds)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, help='Video file to upload')
    parser.add_argument('--title', help='Video title', default='Test Title')
    parser.add_argument('--description', help='Video description', default='Test Description')
    parser.add_argument('--category', default='22', help='Numeric video category.')
    parser.add_argument('--keywords', help='Video keywords, comma separated', default='')
    parser.add_argument('--privacyStatus', choices=VALID_PRIVACY_STATUSES, default='private', help='Video privacy status.')
    args = parser.parse_args()

    youtube = get_authenticated_service()

    try:
        initialize_upload(youtube, args)
    except HttpError as e:
        print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
