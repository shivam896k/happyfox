from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
import base64
from bs4 import BeautifulSoup
import dateutil.parser as parser


class EmailHelper:
    def __init__(self) -> None:
        self.SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
        self.store = file.Storage('storage.json')
        self.creds = self.store.get()
        if not self.creds or self.creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', self.SCOPES)
            self.creds = tools.run_flow(flow, self.store)
        self.gmail = discovery.build('gmail', 'v1', http=self.creds.authorize(Http()))

        self.user_id =  'me'
        self.label_id_inbox = 'INBOX'
        self.label_id_unread = 'UNREAD'

    def get_emails(self):
        unread_msgs = self.gmail.users().messages().list(userId='me',labelIds=[self.label_id_inbox, self.label_id_unread]).execute()
        all_data = []
        email_list = unread_msgs.get('messages', [])
        for email in email_list:
            email_data = {}
            email_id = email['id']
            message = self.gmail.users().messages().get(userId=self.user_id, id=email_id).execute()
            payload = message['payload'] 
            headers = payload['headers']

            email_data['message_id'] = email_id
            for header in headers:
                if header['name'] == 'From':
                    msg_from = header['value']
                    email_data['from_email'] = msg_from
                elif header['name'] == 'To':
                    msg_subject = header['value']
                    email_data['to_email'] = msg_subject
                elif header['name'] == 'Subject':
                    msg_subject = header['value']
                    email_data['subject'] = msg_subject
                elif header['name'] == 'Date':
                    msg_date = header['value']
                    date_parse = (parser.parse(msg_date))
                    m_date = (date_parse.date())
                    email_data['received_at'] = str(m_date)
            try:
                parts = payload.get('parts')[0] 
                print('parts', parts)
                data = parts['body']['data'] 
                data = data.replace("-","+").replace("_","/") 
                decoded_data = base64.b64decode(data) 
                soup = BeautifulSoup(decoded_data , "lxml")
                # soup = BeautifulSoup(decoded_data , "html.parser")
                email_body = soup.body()
                email_data['message'] = email_body
            except Exception as e:
                print(f"Exception occured: {e}")
            all_data.append(email_data)
        return all_data

    def mark_email_as_read(self, email_id):
        self.gmail.users().messages().modify(userId=self.user_id, id=email_id, body={'removeLabelIds': ['UNREAD']}).execute()

    def mark_email_as_unread(self, email_id):
        self.gmail.users().messages().modify(userId=self.user_id, id=email_id, body={'addLabelIds': ['UNREAD']}).execute()
    
    def email_action(self, email_id, body):
        self.gmail.users().messages().modify(userId=self.user_id, id=email_id, body=body).execute()
