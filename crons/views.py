from datetime import datetime, timedelta
import json
import pytz
import channels

from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.throttling import AnonRateThrottle
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from chats.models import Chat, Message, ChatPerson
from projects.models import Project, Person, Collaborator
from projects.serializers import ProjectSerializer
from subscriptions.upgrade_email import upgrade_emailer


class PurgeOldMessages(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        data = []
        now = datetime.now().replace(tzinfo=pytz.UTC)

        for chat in Chat.objects.all():
            chat_data = {}
            chat_data['message_history'] = chat.project.message_history

            for message in Message.objects.filter(chat=chat):
                if message.created < now - timedelta(days=chat.project.message_history):
                    if chat_data.get('deleted_message_stamps', False):
                        chat_data['deleted_message_stamps'].append(message.created)
                    else:
                        chat_data['deleted_message_stamps'] = [message.created]
                    message.delete()

                else:
                    if chat_data.get('good_message_stamps', False):
                        chat_data['good_message_stamps'].append(message.created)
                    else:
                        chat_data['good_message_stamps'] = [message.created]

            data.append(chat_data)

        return Response(data, status=status.HTTP_200_OK)

class ApplyChatUpdates(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request):
        for chat in Chat.objects.all():
            query = Message.objects.filter(chat=chat)
            message = query.latest('created') if len(query) > 0 else None

            for chat_person in ChatPerson.objects.filter(chat=chat):
                if message is not None:
                    chat_person.chat_updated = message.created
                else:
                    chat_person.chat_updated = chat.created
                chat_person.save()

        return Response({'message': 'ok'}, status=status.HTTP_200_OK)


class SyncMemberIDs(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request):
        data = {}
        for chat_person in ChatPerson.objects.all():
            members_ids = json.loads(chat_person.chat.members_ids)
            if chat_person.person.pk not in members_ids:
                members_ids = sorted(members_ids + [chat_person.person.pk])
            chat_person.chat.members_ids = str(members_ids)
            chat_person.chat.save()
            data[chat_person.chat.pk] = str(members_ids)
        return Response(data, status=status.HTTP_200_OK)


class PruneBusinessChat(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request):
        project = Project.objects.get(public_key='a52241fb-be96-4763-8460-a97d46c979a2')
        count = 0
        for person in Person.objects.filter(project=project):
            if len(person.username) > 90:
                person.delete()
                count += 1
        return Response({count: count}, status=status.HTTP_200_OK)


class ReceiveBuffer(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request):
        receive_buffer = channels.layers.channel_layers.backends['default'].receive_buffer
        return Response(
            {
                "mem": str(receive_buffer),
                "len": len(str(receive_buffer).split(',')),
            },
            status=status.HTTP_200_OK
        )


class OwnerToAdmin(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request):
        admins = []
        for project in Project.objects.all():
            collaborator = Collaborator.objects.create(
                user=project.owner,
                project=project,
                role='admin'
            )
            admins.append(str(collaborator))

        return Response({"admins": admins}, status=status.HTTP_200_OK)


personal_email_data = [
    '@gmail.',
    '.edu',
    'mail.ru',
    'icloud.com',
    '@yahoo',
    '@hotmail',
    '@live.',
    '@outlook.',
    'mail.com',
    'example.com',
    '@protonmail.com',
    'gmial.com',
    '.ac.in',
    '@yandex',
    '@qq.com',
    '@naver.com',
]


class BusinessAccounts(APIView):
    throttle_classes = [AnonRateThrottle]
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    def get(self, request):
        if request.user.email != 'upgrader@chatengine.io':
            return Response({'message': 'wrong user...'}, status=status.HTTP_400_BAD_REQUEST)

        users = []
        for user in User.objects.all().order_by('-created'):
            if not any(ext in user.email for ext in personal_email_data):
                user_data = '{} - {}'.format(user.email, user.created)
                users.append(user_data)

        return Response(users, status=status.HTTP_200_OK)


class EndTrialsCron(APIView):
    throttle_classes = [AnonRateThrottle]
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, days):
        now = datetime.now().replace(tzinfo=pytz.UTC)
        end_date = now - timedelta(days=int(days))
        projects = Project.objects.filter(
            is_active=True,
            plan_type='basic',
            created__lte=end_date,
        )
        for project in projects:
            project.is_active = False 
            project.save()
            upgrade_emailer.email_project_is_inactive(project=project)

        serializer = ProjectSerializer(projects, many=True)
        upgrade_emailer.email_json(to_email='adam@lamorre.co', content=len(serializer.data))
        return Response(serializer.data, status=status.HTTP_200_OK)

def email_total_payments(amount: str, payments: json):
    from server.settings import get_secret
    import sendgrid
    # Setup SendGrid
    sg = sendgrid.SendGridAPIClient(get_secret('SEND_GRID_KEY'))
    message = sendgrid.Mail(
        from_email='no_reply@chatengine.io',
        to_emails='adam@lamorre.co',
        subject='Edward has generated ${} in revenue this month!'.format(amount),
        html_content=json.dumps(payments)
    )
    return sg.send(message).status_code

def safe_get_proj(sub):
    try:
        return Project.objects.get(subscription_id=sub)
    except Project.DoesNotExist:
        return None
class PayoutPartnersCron(APIView):
    throttle_classes = [AnonRateThrottle]
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request):
        import datetime, stripe
        from server.settings import get_secret
        stripe.api_key = get_secret("STRIPE_KEY")

        start_date = datetime.datetime.now() - datetime.timedelta(days=31)
        end_date = datetime.datetime.now()
        payments = stripe.PaymentIntent.list(created={"gte": start_date, "lte": end_date})
        partner_payments = []
        for payment in payments.get('data'):
            customer = stripe.Customer.retrieve(id=payment.get("customer"))
            if len(customer.get("subscriptions").get("data")) > 0:
                subscription_id = customer.get("subscriptions").get("data")[0].get('id')
                project = safe_get_proj(sub=subscription_id)
                if project and project.promo_code and project.promo_code.lower() == 'edward':
                    partner_payments.append({"created": payment.created, "amount": payment.amount, "status": payment.status, "subscription_id": subscription_id})
        total = sum(p['amount'] if p['status'] == 'succeeded' else 0 for p in partner_payments)
        status = email_total_payments(amount=str((total * 10**-2)), payments=partner_payments)

        return Response({"status": status}, status=status)
