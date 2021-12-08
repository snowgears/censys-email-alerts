from __future__ import print_function
import os.path
import base64
import pickle
from datetime import datetime, date

from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from censys.asm import Events, HostsAssets
from censys.common.exceptions import CensysHostNotFoundException

import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio

# --- variables ---

MAIL_RECIPIENTS = ['awesomete@gmail.com']
MAIL_SUBJECT = "[Censys Alerts] New host risks discovered."
MAIL_BODY = "Attached is a csv of all new host risks that were discovered."

IGNORE_LASTRUN = True

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.compose', 'https://www.googleapis.com/auth/gmail.send']


# --- functions ---

def load_lastrun():
    try:
        with open ('lastrun', 'rb') as fp:
            return pickle.load(fp)
    except FileNotFoundError:
        return None


def save_lastrun():
    with open('lastrun', 'wb') as fp:
        ct = datetime.now()
        ct_formatted = ct.strftime('%Y-%m-%dT%H:%M:%SZ')
        pickle.dump(ct_formatted, fp)

def get_gmail_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    print(os.path.abspath('token.json'))
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def create_message(sender, to, subject, message_text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject

  b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
  b64_string = b64_bytes.decode()
  return {'raw': b64_string}

def create_message_with_attachment(sender, to, subject, message_text, file):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.
      file: The path to the file to be attached.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    content_type, encoding = mimetypes.guess_type(file)

    if content_type is None or encoding is not None:
      content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
      fp = open(file, 'rb')
      msg = MIMEText(fp.read(), _subtype=sub_type)
      fp.close()
    elif main_type == 'image':
      fp = open(file, 'rb')
      msg = MIMEImage(fp.read(), _subtype=sub_type)
      fp.close()
    elif main_type == 'audio':
      fp = open(file, 'rb')
      msg = MIMEAudio(fp.read(), _subtype=sub_type)
      fp.close()
    else:
      fp = open(file, 'rb')
      msg = MIMEBase(main_type, sub_type)
      msg.set_payload(fp.read())
      fp.close()
    filename = os.path.basename(file)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
    b64_string = b64_bytes.decode()
    return {'raw': b64_string}

def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    print ('Message Id: %s' % message['id'])
    return message
  except HttpError as error:
    print ('An error occurred: %s' % error)

def get_host_risks():
  e = Events()
  h = HostsAssets()

  lastrun = load_lastrun()
  if IGNORE_LASTRUN:
    lastrun = None

  if lastrun == None:
    print("Getting all added host risks.")
    cursor = e.get_cursor(filters=["HOST_RISK"])
  else:
    print("Getting all added host risks since "+lastrun)
    cursor = e.get_cursor(lastrun, filters=["HOST_RISK"])

  events = e.get_events(cursor)
  save_lastrun()

  host_risks = {}
  for event in events:
    # only show logbook events with the 'add' tag
    if event["operation"] == "ADD":
        print(event)
        host_risks[event["entity"]["ipAddress"]] = event["data"]["title"]
        # try:
        #     # enrich the data of this host_risk with more data from the host itself
        #     host = h.get_asset_by_id(event["entity"]["ipAddress"])
        #     print(host)
        # except CensysHostNotFoundException:
        #     pass
  return host_risks

def build_csv(dict):
  with open('host-risks.csv', 'w') as f:
      for key in dict.keys():
        f.write("%s,%s\n"%(key,dict[key]))
      return ('host-risks.csv', f.read(), 'text/csv')

# --- main thread ---

if __name__ == '__main__':

    # TODO
    # kick off thread where we check every X minutes for new host risks

    # get censys host risks
    host_risks = get_host_risks()

    # TODO check if host risks was populated with data
    # (if no new data, return)

    # build the csv from the host risks dict
    risks_csv = build_csv(host_risks)


    service = get_gmail_service()

    # get the google profile of the user that gave us their permission to send emails on their behalf
    profile = service.users().getProfile(userId='me').execute()
    print ('Email we will be sending from: %s' % profile['emailAddress'])

    for recipient in MAIL_RECIPIENTS:
        message = create_message(profile['emailAddress'], recipient, MAIL_SUBJECT, MAIL_BODY)
        message = create_message_with_attachment(profile['emailAddress'], recipient, MAIL_SUBJECT, MAIL_BODY, risks_csv)
        #print ('Message: %s' % message)
        send_message(service, "me", message)
        print ('Sent email alert to: %s' % recipient)