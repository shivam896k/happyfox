from django.core.management.base import BaseCommand
from email_operations.utils.email_helpers import EmailHelper
from email_operations.utils.rule_service import RuleHelper
from email_operations.models import Mail

class Command(BaseCommand):
    help = 'Processes email based on criteria.'

    def add_arguments(self, parser):
        parser.add_argument('rule', type=str, help='Which rule to perform action on.')


    def handle(self, *args, **kwargs):
        rule = kwargs['rule']
        rule_helper = RuleHelper(rule)
        result = rule_helper.apply_rule()
        rule_helper.apply_action(result)
