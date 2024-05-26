import base64
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from email_operations.utils.email_helpers import EmailHelper


class EmailHelperTests(TestCase):

    def setUp(self):
        self.email_helper = EmailHelper()

    @patch('email_operations.utils.email_helpers.discovery.build')
    @patch('email_operations.utils.email_helpers.file.Storage')
    @patch('email_operations.utils.email_helpers.client.flow_from_clientsecrets')
    @patch('email_operations.utils.email_helpers.tools.run_flow')
    def test_init(self, mock_run_flow, mock_flow_from_clientsecrets, mock_storage, mock_build):
        mock_creds = MagicMock()
        mock_storage.return_value.get.return_value = mock_creds
        mock_creds.invalid = False
        
        email_helper = EmailHelper()
        
        mock_storage.assert_called_with('storage.json')
        mock_storage.return_value.get.assert_called_once()
        mock_build.assert_called_with('gmail', 'v1', http=mock_creds.authorize.return_value)
        
        self.assertEqual(email_helper.user_id, 'me')
        self.assertEqual(email_helper.label_id_inbox, 'INBOX')
        self.assertEqual(email_helper.label_id_unread, 'UNREAD')

    @patch('email_operations.utils.email_helpers.discovery.build')
    def test_get_emails(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        mock_service.users().messages().list().execute.return_value = {
            'messages': [{'id': '123'}]
        }
        
        mock_service.users().messages().get().execute.return_value = {
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'test@example.com'},
                    {'name': 'To', 'value': 'me@example.com'},
                    {'name': 'Subject', 'value': 'Test Subject'},
                    {'name': 'Date', 'value': 'Fri, 01 Jan 2021 12:00:00 -0000'}
                ],
                'body': {'data': base64.urlsafe_b64encode(b'test message').decode('ascii')}
            }
        }
        
        emails = self.email_helper.get_emails()
        
        self.assertEqual(len(emails), 1)
        email = emails[0]
        self.assertEqual(email['message_id'], '123')
        self.assertEqual(email['from_email'], 'test@example.com')
        self.assertEqual(email['to_email'], 'me@example.com')
        self.assertEqual(email['subject'], 'Test Subject')
        self.assertEqual(email['received_at'], '2021-01-01')
        self.assertEqual(email['message'], 'test message')

    @patch('email_operations.utils.email_helpers.discovery.build')
    def test_mark_email_as_read(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        self.email_helper.mark_email_as_read('123')
        
        mock_service.users().messages().modify.assert_called_with(
            userId='me', id='123', body={'removeLabelIds': ['UNREAD']}
        )
        mock_service.users().messages().modify.return_value.execute.assert_called_once()

    @patch('email_operations.utils.email_helpers.discovery.build')
    def test_mark_email_as_unread(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        self.email_helper.mark_email_as_unread('123')
        
        mock_service.users().messages().modify.assert_called_with(
            userId='me', id='123', body={'addLabelIds': ['UNREAD']}
        )
        mock_service.users().messages().modify.return_value.execute.assert_called_once()

    @patch('email_operations.utils.email_helpers.discovery.build')
    def test_email_action(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        body = {'addLabelIds': ['IMPORTANT']}
        self.email_helper.email_action('123', body)
        
        mock_service.users().messages().modify.assert_called_with(
            userId='me', id='123', body=body
        )
        mock_service.users().messages().modify.return_value.execute.assert_called_once()
