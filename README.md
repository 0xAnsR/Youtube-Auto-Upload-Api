# OAuth 2.0 Configuration for YouTube Video Upload

## Overview

This document provides the setup for OAuth 2.0 credentials required for integrating with the YouTube API, specifically for uploading videos. It includes details for using GitHub Codespaces as the development environment.

## Credentials

Here are the OAuth 2.0 credentials used for this setup:

- **Client ID**: `715144864465-0si1ip7sqslli3ptg14ktl7mc0f71dqe.apps.googleusercontent.com`
- **Client Secret**: `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`
- **Redirect URI**: `https://glowing-yodel-55j94rx6qg5c4j77.github.dev/oauth2callback`

## Steps to Configure OAuth 2.0

### 1. Set Up Redirect URI in Google Cloud Console

1. Log in to the [Google Cloud Console](https://console.cloud.google.com/).
2. Navigate to **APIs & Services** > **Credentials**.
3. Locate your OAuth 2.0 Client ID and click **Edit**.
4. In the **Authorized redirect URIs** section, add:
   
https://glowing-yodel-55j94rx6qg5c4j77.github.dev/oauth2callback

markdown
Copy code

5. Save your changes.

### 2. Configure Your Application

Ensure your application has a route to handle requests at `/oauth2callback`. This route should manage the OAuth 2.0 callback process, including:

- Extracting the authorization code from the callback URL.
- Exchanging the authorization code for an access token using the Google OAuth 2.0 token endpoint.

### 3. Testing and Debugging

1. **Authorize Application**:
- Open the following URL in your browser to start the authorization process:

  ```
  https://accounts.google.com/o/oauth2/auth
    ?response_type=code
    &client_id=715144864465-0si1ip7sqslli3ptg14ktl7mc0f71dqe.apps.googleusercontent.com
    &redirect_uri=https://glowing-yodel-55j94rx6qg5c4j77.github.dev/oauth2callback
    &scope=https://www.googleapis.com/auth/youtube.upload
    &access_type=offline
  ```

2. **Extract Authorization Code**:
- After authorizing the application, you will be redirected to `https://glowing-yodel-55j94rx6qg5c4j77.github.dev/oauth2callback` with an authorization code in the URL. Extract this code.

3. **Exchange Authorization Code for Access Token**:
- Use `curl` or another HTTP client to exchange the authorization code for an access token:

  ```bash
  curl -X POST https://oauth2.googleapis.com/token \
    -d "code=YOUR_AUTHORIZATION_CODE" \
    -d "client_id=715144864465-0si1ip7sqslli3ptg14ktl7mc0f71dqe.apps.googleusercontent.com" \
    -d "client_secret=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" \
    -d "redirect_uri=https://glowing-yodel-55j94rx6qg5c4j77.github.dev/oauth2callback" \
    -d "grant_type=authorization_code"
  ```

- Replace `YOUR_AUTHORIZATION_CODE` with the actual code you obtained.

## Notes

- **Redirect URI**: Ensure the redirect URI in your Google Cloud Console matches the one used in your application. If the URL of your Codespace changes, you will need to update this URI accordingly.
- **OAuth Scopes**: Adjust the `scope` parameter in the authorization URL based on the specific permissions your application requires.
When using Google OAuth in a Codespace (or any environment where localhost might not be accessible), you may encounter issues with the redirect URI. Here are some steps you can take to resolve this:

1. Update the Redirect URI
In your Google Cloud Console:

Go to Credentials and find the OAuth 2.0 client ID you're using.
Under Authorized redirect URIs, add the specific URL provided by Codespaces (usually something like https://<your-codespace>.preview.app/...) instead of http://localhost:8080.
2. Use the run_console Method
If you can't change the redirect URI easily, you can modify the code to use the console method for authentication. Change this line in the get_authenticated_service function:

python
Copy code
credentials = flow.run_local_server()
to:

python
Copy code
credentials = flow.run_console()
This will prompt you to manually enter the authorization code after visiting the URL.

3. Environment Configuration
Make sure your environment is set up correctly to handle the OAuth flow. Sometimes, using a different port or ensuring that your Codespace allows inbound connections is necessary.

4. Test the Setup
Once you make the changes, run your script again, and follow the prompts. You should be able to authenticate and upload your video.

Let me know if you need further assistance!


By following these steps, you should be able to integrate OAuth 2.0 with the YouTube API for video uploads using GitHub Codespaces.

For more information on OAuth 2.0 setup and configuration, refer to the [Google OAuth 2.0 documentation](https://developers.google.com/identity/protocols/oauth2).
This README.md file includes all the necessary details for configuring OAuth 2.0 in your GitHub Codespace and provides guidance on setting up the redirect URI, obtaining the authorization code, and exchanging it for an access token.
