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
    - Note: create credentials.json file for your gmail service and then run this command.
    - Example `python manage.py process_email rule1`
    - Based on the rule defined in rule.json it will do the operation.


## Due to some technical issue I am not able to record my voice. that's why I haven't created the code implementation demo. Have wrote my code structure in below paragraph.

### Project structure
- In `models.py` file table structure is defined.
- In `utils/email_helper.py` email helper methods such as `fetch email` operation is defined.
- In `utils/rule_service.py` rule based operations such as `apply_rule` and `apply_action` is defined which is responsible for getting email entries based on rule and applying action on them.
- python script `fetch_email.py` is responsible for fetching emails and storing it in db.
- python script `process_email.py` is responsible for doing filter based on `rule.json` and applying appropriate action on them. 

### Demo video
[![Watch the video](https://www.youtube.com/watch?v=J2DRbrixkJ8&ab_channel=ShivamSingh)](https://www.youtube.com/watch?v=J2DRbrixkJ8&ab_channel=ShivamSingh)
