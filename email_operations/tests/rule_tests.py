import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.db.models import Q
from email_operations.models import Mail
from email_operations.utils.email_helpers import EmailHelper
from email_operations.utils.email_helpers import RuleHelper

class RuleHelperTests(TestCase):

    def setUp(self):
        self.rule_data = {
            "test_rule": {
                "predicate": "ALL",
                "criteria": [
                    {"name": "from_email", "action": "contains", "value": "example.com"},
                    {"name": "received_at", "action": "less than", "value": 30}
                ],
                "action": {
                    "add_tag": ["UNREAD"],
                    "remove_tag": []
                }
            }
        }
        
        self.rules_path = '/home/shivam/projects/happyfox/rules.json'
        with open(self.rules_path, 'w') as f:
            json.dump(self.rule_data, f)

    def test_init_with_invalid_rule(self):
        with self.assertRaises(Exception) as context:
            RuleHelper(None)
        self.assertTrue('Rule and path are required' in str(context.exception))

    def test_init_with_invalid_path(self):
        with self.assertRaises(Exception) as context:
            RuleHelper('test_rule', None)
        self.assertTrue('Rule and path are required' in str(context.exception))

    def test_init_with_invalid_predicate(self):
        self.rule_data['test_rule']['predicate'] = 'INVALID'
        with open(self.rules_path, 'w') as f:
            json.dump(self.rule_data, f)
        
        with self.assertRaises(Exception) as context:
            RuleHelper('test_rule', path=self.rules_path)
        self.assertTrue('predicate need to be one of (ALl, ANY)' in str(context.exception))

    @patch('email_operations.models.Mail.objects.filter')
    def test_apply_rule_all_predicate(self, mock_filter):
        rule_helper = RuleHelper('test_rule', path=self.rules_path)
        mock_filter.return_value = []
        
        results = rule_helper.apply_rule()
        
        self.assertTrue(mock_filter.called)

    @patch('email_operations.models.Mail.objects.filter')
    def test_apply_rule_any_predicate(self, mock_filter):
        self.rule_data['test_rule']['predicate'] = 'ANY'
        with open(self.rules_path, 'w') as f:
            json.dump(self.rule_data, f)
        
        rule_helper = RuleHelper('test_rule', path=self.rules_path)
        mock_filter.return_value = []
        
        results = rule_helper.apply_rule()
        
        self.assertTrue(mock_filter.called)

    @patch.object(EmailHelper, 'email_action')
    def test_apply_action(self, mock_email_action):
        rule_helper = RuleHelper('test_rule', path=self.rules_path)
        results = [
            MagicMock(message_id="12345"),
            MagicMock(message_id="67890")
        ]
        
        rule_helper.apply_action(results)
        
        self.assertEqual(mock_email_action.call_count, len(results))
        mock_email_action.assert_any_call("12345", {"add_tag": ["important", "work"], "remove_tag": ["personal"]})
        mock_email_action.assert_any_call("67890", {"add_tag": ["important", "work"], "remove_tag": ["personal"]})

    def test_string_fields_validation(self):
        self.rule_data['test_rule']['criteria'][0]['action'] = 'invalid_action'
        with open(self.rules_path, 'w') as f:
            json.dump(self.rule_data, f)
        
        with self.assertRaises(Exception) as context:
            RuleHelper('test_rule', path=self.rules_path)
        self.assertTrue('Invalid action provided.' in str(context.exception))

    def test_date_fields_validation(self):
        self.rule_data['test_rule']['criteria'][1]['action'] = 'invalid_action'
        with open(self.rules_path, 'w') as f:
            json.dump(self.rule_data, f)
        
        with self.assertRaises(Exception) as context:
            RuleHelper('test_rule', path=self.rules_path)
        self.assertTrue('Invalid action provided.' in str(context.exception))

    def test_get_query_filter_name(self):
        rule_helper = RuleHelper('test_rule', path=self.rules_path)
        self.assertEqual(rule_helper.get_query_filter_name('contains'), 'contains')
        self.assertEqual(rule_helper.get_query_filter_name('does not contain'), 'notcontains')
        self.assertEqual(rule_helper.get_query_filter_name('equals'), 'exact')
        self.assertEqual(rule_helper.get_query_filter_name('does not equals'), '~')
        self.assertEqual(rule_helper.get_query_filter_name('less than'), 'lt')
        self.assertEqual(rule_helper.get_query_filter_name('greater than'), 'gt')

