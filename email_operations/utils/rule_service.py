import json
from email_operations.models import Mail
from datetime import datetime, timedelta
from django.db.models import Q
from email_operations.utils.email_helpers import EmailHelper


class RuleHelper:
    def __init__(self, rule, path='/home/shivam/projects/happyfox/rules.json'):
        if not rule or not path:
            raise Exception('Rule and path are required')

        rules = json.load(open(path))
        self.rule = rules[rule]
        self.predicate = self.rule['predicate']
        if self.predicate not in ['ALL', 'ANY']:
            raise Exception('predicate need to be one of (ALl, ANY)')
        self.criterias = self.rule['criteria']
        self.actions = self.rule['action']

    def apply_rule(self):
        query = Q()
        if self.predicate == 'ALL':
            for criteria in self.criterias:
                if criteria['name'] in self._string_fields():
                    if self.get_query_filter_name(criteria['action']) == '~':
                        query &= ~Q(**{f"{criteria['name']}__{criteria['action']}": criteria['value']})
                    else:
                        query &= Q(**{f"{criteria['name']}__{criteria['action']}": criteria['value']})
                elif criteria['name'] in self._date_fields():
                    query &= Q(**{f"{criteria['name']}__{criteria['action']}": datetime.now() - timedelta(days=criteria['value'])})
        elif self.predicate == 'ANY':
            for criteria in self.criterias:
                if criteria['name'] in self._string_fields():
                    if self.get_query_filter_name(criteria['action']) == '~':
                        query |= ~Q(**{f"{criteria['name']}__{criteria['action']}": criteria['value']})
                    else:
                        query |= Q(**{f"{criteria['name']}__{criteria['action']}": criteria['value']})
                elif criteria['name'] in self._date_fields():
                    query |= Q(**{f"{criteria['name']}__{criteria['action']}": datetime.now() - timedelta(days=criteria['value'])})
        
        return Mail.objects.filter(query)

    def apply_action(self, results):
        email_helper = EmailHelper()
        for result in results:
            email_id = result.message_id
            body = {}
            for action, tags in self.actions.items():
                if body.get(action, None):
                    body[action] += tags
                else:
                    body[action] = tags
            email_helper.email_action(email_id, body)

    def _string_fields(self):
        for criteria in self.criterias:
            if criteria.get('action') not in ['contains', 'does not contain', 'equals', 'does not equals']:
                raise Exception('Invalid action provided.')
        return ['from_email', 'to_email', 'subject', 'message']

    def _date_fields(self):
        for criteria in self.criterias:
            if criteria.get('action') not in ['less than', 'greater than']:
                raise Exception('Invalid action provided.')
        return ['received_at']

    def get_query_filter_name(self, name):
        filter_name_mapping = {
            'contains': 'contains',
            'does not contain': 'notcontains',
            'equals': 'exact',
            'does not equals': '~',
            'less than': 'lt',
            'greater than': 'gt'
        }
        return filter_name_mapping[name]

