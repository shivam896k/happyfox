# Happyfox assignment
A standalone Python script that integrates with Gmail API and performs some rule based operations on emails.

### setup steps
- Run `pip install -r requirements.txt`
    - Install all the requirements for the procjet.
- Run `python manage.py migrate`
    - Create necessary tables in db.
- Run `python manage.py feth_emails`
    - fetch emails for the account specified.
- Run `python manage.py process_email <rule_name>`
    - Example `python manage.py process_email rule1`
    - Based on the rule defined in rule.json it will do the operation.

### Demo video
[![Watch the video](https://github.com/shivam896k/happyfox/blob/main/demo.mkv)](https://github.com/shivam896k/happyfox/blob/main/demo.mkv)
