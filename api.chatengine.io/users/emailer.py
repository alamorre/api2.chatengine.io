from projects.models import Project
from server.settings import os

import sendgrid

sg = sendgrid.SendGridAPIClient(os.getenv('SEND_GRID_KEY'))

class Emailer():
    def __init__(self):
        pass

    def email_user_limit(self, project: Project):
        try:
            message = sendgrid.Mail(
                from_email='no_reply@chatengine.io',
                to_emails=[str(project.owner)],
                subject='Chat Engine | User limit reached',
                html_content="""
                You reached for user limit for the following Chat Engine project:<br/><br/>
                <div>Project ID: {}<br/>
                Project Title: {}<br/>
                Owner: {}<br/>
                Limit: {}<br/>
                Plan: {}</div>""".format(
                    str(project.public_key), 
                    project.title, 
                    project.owner,
                    str(project.monthly_users),
                    project.plan_type
                )
            )
            sg.send(message)
        except Exception as e:
            print(e)

emailer = Emailer()