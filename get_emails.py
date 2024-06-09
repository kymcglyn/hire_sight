import os.path
import webbrowser 
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.utils import parsedate_to_datetime

webbrowser.register('chrome', None, webbrowser.GenericBrowser('C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'))

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API to list messages
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me").execute()
        messages = results.get("messages", [])

        if not messages:
            print("No messages found.")
            return
        
        print("Messages:")
        for message in messages:
            message_id = message["id"]
            msg = service.users().messages().get(userId="me", id=message_id).execute()
            message_payload = msg["payload"]
            headers = message_payload["headers"]
            subject = [header["value"] for header in headers if header["name"] == "Subject"][0]
            sender = [header["value"] for header in headers if header["name"] == "From"][0]
            date_str = [header["value"] for header in headers if header["name"] == "Date"][0]
            received_date = parsedate_to_datetime(date_str)
            print("Subject:", subject)
            print("From:", sender)
            print("Received Date:", received_date.strftime("%Y-%m-%d %H:%M:%S"))
            
            # Check if the message has a body
            if "parts" in message_payload:
                parts = message_payload["parts"]
                for part in parts:
                    if part["mimeType"] == "text/plain":
                        data = part["body"]["data"]
                        body = base64.urlsafe_b64decode(data).decode("utf-8")
                        print("Body:", body)
                        break
            else:
                print("No body found.")

    except HttpError as error:
        # Handle errors from Gmail API
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
