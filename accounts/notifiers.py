# todo: Implement this

# from python_http_client.exceptions import HTTPError

# import sendgrid

# from accounts.models import User, Reset
# from server.settings import get_secret

# sg = sendgrid.SendGridAPIClient(get_secret('SEND_GRID_KEY'))


# class Emailer():
#     def __init__(self):
#         pass

#     def email_mfa_code(self, user: User):
#         data = {
#             "personalizations": [
#                 {
#                     "to": [{"email": user.email}],
#                     "subject": "MFA Code | Chat Engine",
#                     "substitutions": {
#                         "-mfa_code-": str(user.mfa_code)
#                     }
#                 }
#             ],
#             "from": {"email": 'no_reply@chatengine.io'},
#             "template_id": "a318cb88-9115-44ad-aeca-2f6b6ab5c301"
#         }
#         try:
#             sg.client.mail.send.post(request_body=data)
#             return True
#         except HTTPError:
#             return False

#     def email_reset_link(self, user: User, reset: Reset):
#         link = 'https://chatengine.io/reset/{}'.format(str(reset.uuid)) \
#             if get_secret('PIPELINE') == 'production' else \
#             'http://localhost:3000/reset/{}'.format(str(reset.uuid))

#         data = {
#             "personalizations": [
#                 {
#                     "to": [{"email": user.email}],
#                     "subject": "Reset Password | Chat Engine",
#                     "substitutions": {
#                         "-link-": link
#                     }
#                 }
#             ],
#             "from": {"email": 'no_reply@chatengine.io'},
#             "template_id": "02e2e343-03b3-4bee-a6b1-3e7527a3b207"
#         }

#         try:
#             sg.client.mail.send.post(request_body=data)
#             return True

#         except HTTPError:
#             return False
