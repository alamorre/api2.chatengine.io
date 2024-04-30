import pytz, json, os
from datetime import datetime, timedelta

from python_http_client.exceptions import HTTPError

from projects.models import Project

import sendgrid

sg = sendgrid.SendGridAPIClient(os.getenv('SEND_GRID_KEY'))

class Emailer():
    def __init__(self):
        pass

    def email_trial_created(self, project: Project):
        # message = sendgrid.Mail(
        #     from_email='no_reply@chatengine.io',
        #     to_emails='adam@lamorre.co',
        #     subject='New CE trial is on!',
        #     html_content='<p>{} started a trial for {} and is_active == {}</p>'.format(
        #         str(project.owner), 
        #         project.title, 
        #         str(project.is_active)
        #     )
        # )
        # try:
        #     sg.send(message)
        # except Exception as e:
        #     print(e.message)
        pass

    def email_subscription_delete_failed(self, project: Project):
        message = sendgrid.Mail(
            from_email='no_reply@chatengine.io',
            to_emails='adam@lamorre.co',
            subject='Subscription delete failed',
            html_content='<p>{} deleted sub for {} but {} cannot be found</p>'.format(
                str(project.owner), 
                project.title, 
                project.subscription_id
            )
        )
        try:
            sg.send(message)
        except Exception as e:
            print(e.message)

    def email_project_is_inactive(self, project: Project):
        last_project_inactive_email = project.last_project_inactive_email
        now = datetime.now().replace(tzinfo=pytz.UTC)
        if last_project_inactive_email is None \
            or now > last_project_inactive_email + timedelta(days=1):
            link = '{}/projects/{}'.format(os.getenv('WEBSITE_URL'), project.public_key)
            data = {
                "personalizations": [
                    {
                        "to": [{"email": project.owner.email}],
                        "subject": "Chat Engine | Project is Deactivated",
                        "substitutions": {
                            "-title-": project.title,
                            "-link-": link,
                        }
                    }
                ],
                "from": {"email": 'no_reply@chatengine.io'},
                "template_id": "ee194293-a2a9-49c2-8afd-6148f780fab4"
            }
        try:
            sg.client.mail.send.post(request_body=data)
            project.last_project_inactive_email = now 
            project.save()
        except HTTPError:
            pass

    def email_json(self, to_email: str, content:str=None):
        data = {
            "personalizations": [
                {
                    "to": [{"email": to_email}],
                    "subject": "Chat Engine | Ended Trials",
                }
            ],
            "from": {"email": 'no_reply@chatengine.io'},
            "content": [
                {
                    "type": "text/plain",
                    "value": json.dumps(content, indent=2, separators=(',', ': '))
                }
            ]
        }
        try:
            sg.client.mail.send.post(request_body=data)
        except HTTPError:
            pass
    
    def email_subscription_deleted(self, subscription_id):
        # message = sendgrid.Mail(
        #     from_email='no_reply@chatengine.io',
        #     to_emails='adam@lamorre.co',
        #     subject='CE subscription deleted...',
        #     html_content=subscription_id
        # )
        # try:
        #     sg.send(message)
        # except Exception as e:
        #     print(e.message)
        pass

upgrade_emailer = Emailer()