from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.utils import parsedate_to_datetime
import base64

# Provide your credentials here
creds = Credentials.from_authorized_user_file("token.json")

# Create a service object for the Gmail API
service = build("gmail", "v1", credentials=creds)

# Specify the user ID (usually "me" for the authenticated user)
user_id = "kmcglynn20@gmail.com"

try:
    # Initialize an empty list to store all messages
    all_messages = []

    # Call the Gmail API to list messages
    response = service.users().messages().list(userId=user_id).execute()

    # Extract messages from the response
    messages = response.get("messages", [])

    # Add the first batch of messages to the list
    all_messages.extend(messages)

    # If there are more messages to fetch, keep retrieving them
    counter = 0
    while "nextPageToken" in response and counter < 10:
        next_page_token = response["nextPageToken"]
        
        # Call the Gmail API to list messages with the next page token
        response = service.users().messages().list(userId=user_id, pageToken=next_page_token).execute()
        
        # Extract messages from the response and add them to the list
        messages = response.get("messages", [])
        all_messages.extend(messages)
        counter += 1
    # Print the total number of messages retrieved
    print(f"Total number of messages retrieved: {len(all_messages)}")
    print(all_messages)

    print("Messages:")
    for message in all_messages:
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
except Exception as e:
    print("An error occurred:", e)
