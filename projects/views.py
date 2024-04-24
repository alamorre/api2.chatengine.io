import uuid, pytz, os
from datetime import datetime, timedelta

import stripe 

from rest_framework.throttling import UserRateThrottle
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404, redirect

from accounts.models import User

from chats.models import Chat, ChatPerson, Message
from chats.serializers import ChatSerializer

from users.emailer import emailer

from .models import Collaborator, Invite, Person, Promo
from .serializers import InviteSerializer, ProjectSerializer, PersonSerializer, CollaboratorSerializer
from .authentication import TokenProjectAuthentication

def get_promo_or_none(code: str):
    try:
        return Promo.objects.get(code=code)
    except Promo.DoesNotExist:
        return None

class Projects(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenProjectAuthentication,)

    def get(self, request):
        collaborators = Collaborator.objects.filter(user=request.user)
        projects = [collaborator.project for collaborator in collaborators]
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            default_expires_date = (datetime.now().replace(tzinfo=pytz.UTC) + timedelta(days=10)).date()
            promo_code = request.data.get('promo_code', None)
            serializer.save(
                owner=request.user, 
                is_active=True, 
                monthly_users=10,
                expires_date=None if get_promo_or_none(code=promo_code) else default_expires_date
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            # try:
            #     project_json = serializer.data
            #     checkout_session = stripe.checkout.Session.create(
            #         billing_address_collection='auto',
            #         line_items=[
            #             { 'price': os.getenv('STRIPE_LIGHT_PLAN', None), 'quantity': 1,},
            #         ],
            #         mode='subscription',
            #         success_url='{}/projects/{}'.format(os.getenv('WEBSITE_URL'), project_json['public_key']),
            #         cancel_url='{}/projects/{}'.format(os.getenv('WEBSITE_URL'), project_json['public_key']),
            #         subscription_data={'trial_period_days': 10 },
            #         metadata={
            #             "project_id": project_json['public_key'], 
            #             "plan_type": "light",
            #             "webhook_secret": os.getenv("STRIPE_WEBHOOK_SECRET")
            #         }
            #     )
            #     data = {"project": project_json, "stripe_link": checkout_session.url}
            #     return Response(data, status=status.HTTP_201_CREATED)
            # except Exception as e:
            #     return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetails(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenProjectAuthentication,)

    def get(self, request, project_id):
        get_object_or_404(Collaborator, user=request.user, project=request.auth)
        project = request.auth
        serializer = ProjectSerializer(project, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, project_id):
        get_object_or_404(Collaborator, user=request.user, project=request.auth)
        project = request.auth
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, project_id):
        get_object_or_404(Collaborator, user=request.user, project=request.auth)
        project = request.auth
        project.delete()
        return Response({"id": project_id}, status=status.HTTP_200_OK)


class MessageCount(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenProjectAuthentication,)

    def get(self, request, project_id):
        get_object_or_404(Collaborator, user=request.user, project=request.auth)
        project = request.auth
        chats = Chat.objects.filter(project=project)
        messages = Message.objects.filter(chat__in=chats)
        return Response({"message_count": len(messages)}, status=status.HTTP_200_OK)


class PrivateKeyDetails(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenProjectAuthentication,)

    def get(self, request, project_id):
        get_object_or_404(Collaborator, user=request.user, project=request.auth)
        project = request.auth
        return Response({"key": project.private_key}, status=status.HTTP_200_OK)

    def patch(self, request, project_id):
        get_object_or_404(Collaborator, user=request.user, project=request.auth)
        project = request.auth
        project.private_key = uuid.uuid1()
        project.save()
        return Response({"key": project.private_key}, status=status.HTTP_200_OK)


class ProjectUpgrade(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenProjectAuthentication,)

    def get(self, request, project_id):
        get_object_or_404(Collaborator, user=request.user, project=request.auth)
        
        project = request.auth
        if project.subscription_id is not None:
            stripe.Subscription.delete(project.subscription_id)
            project.subscription_id = None
            project.save()

        checkout_session = stripe.checkout.Session.create(
            billing_address_collection='auto',
            line_items=[
                { 'price': os.getenv('STRIPE_LIGHT_PLAN', None), 'quantity': 1,},
            ],
            mode='subscription',
            success_url='{}/projects/{}'.format(os.getenv('WEBSITE_URL'), project_id),
            cancel_url='{}/projects/{}'.format(os.getenv('WEBSITE_URL'), project_id),
            metadata={
                "project_id": project_id, 
                "plan_type": "light",
                "webhook_secret": os.getenv("STRIPE_WEBHOOK_SECRET")
            }
        )
        return Response(checkout_session.url, status=status.HTTP_200_OK)

        

class ProjectCollaboratorsWeb(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenProjectAuthentication,)

    def get(self, request, project_id):
        get_object_or_404(Collaborator, user=request.user, project=request.auth)
        serializer = CollaboratorSerializer(request.auth.collaborators, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CollaboratorsDetailsWeb(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenProjectAuthentication,)

    def get(self, request, project_id, collaborator_id):
        get_object_or_404(Collaborator, user=request.user, project=request.auth)
        collaborator = get_object_or_404(Collaborator, id=collaborator_id)
        serializer = CollaboratorSerializer(collaborator, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, project_id, collaborator_id):
        get_object_or_404(Collaborator, user=request.user, project=request.auth, role='admin')

        collaborator = get_object_or_404(Collaborator, id=collaborator_id)
        serializer = CollaboratorSerializer(collaborator, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, project_id, collaborator_id):
        get_object_or_404(Collaborator, user=request.user, project=request.auth, role='admin')
        collaborator = get_object_or_404(Collaborator, id=collaborator_id)
        collaborator_json = CollaboratorSerializer(collaborator, many=False).data
        collaborator.delete()
        return Response(collaborator_json, status=status.HTTP_200_OK)


class ProjectInvitesWeb(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenProjectAuthentication,)

    def get(self, request, project_id):
        get_object_or_404(Collaborator, user=request.user, project=request.auth)
        serializer = InviteSerializer(request.auth.invites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, project_id):
        get_object_or_404(Collaborator, user=request.user, project=request.auth, role='admin')
        serializer = InviteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project=request.auth, to_email=request.data['to_email'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InviteDetailsWeb(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = (permissions.AllowAny,)

    def get(self, request, invite_key):
        invite = get_object_or_404(Invite, access_key=invite_key)
        serializer = InviteSerializer(invite, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, invite_key):
        invite = get_object_or_404(Invite, access_key=invite_key)
        serializer = InviteSerializer(invite, data=request.data, partial=True)
        if serializer.is_valid():
            invite = serializer.save()
            serializer = InviteSerializer(invite, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, invite_key):
        invite = get_object_or_404(Invite, access_key=invite_key)
        user = get_object_or_404(User, email=invite.to_email)
        collaborator, created = Collaborator.objects.get_or_create(
            user=user,
            project=invite.project,
            role=invite.role
        )
        invite.delete()
        serializer = ProjectSerializer(collaborator.project, many=False)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    def delete(self, request, invite_key):
        invite = get_object_or_404(Invite, access_key=invite_key)
        invite_json = InviteSerializer(invite, many=False).data
        invite.delete()
        return Response(invite_json, status=status.HTTP_200_OK)


class ProjectPeopleWeb(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenProjectAuthentication,)

    def get_param(self, request, param, default: int = 0):
        try:
            return int(request.GET.get(param, default))
        except TypeError:
            return 0

    def get(self, request, project_id):
        page = self.get_param(request=request, param='page', default=0)
        page_size = self.get_param(request=request, param='page_size', default=250)
        start = page * page_size
        end = (page * page_size) + page_size
        get_object_or_404(Collaborator, user=request.user, project=request.auth)
        project = request.auth
        people = Person.objects.filter(project=project)[start:end]
        serializer = PersonSerializer(people, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, project_id):
        get_object_or_404(Collaborator, user=request.user, project=request.auth)
        project = request.auth

        if len(Person.objects.filter(project=project)) >= project.monthly_users:
            emailer.email_user_limit(project=project)
            return Response("You're over your user limit.", status=status.HTTP_400_BAD_REQUEST)

        match = Person.objects.filter(project=project, username=request.data.get('username', None))
        if match.exists():
            return Response({'message': "This username is taken."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PersonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PersonDetailsWeb(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenProjectAuthentication,)

    def get(self, request, project_id, person_id):
        get_object_or_404(Collaborator, user=request.user, project=request.auth)
        project = request.auth
        person = get_object_or_404(Person, project=project, pk=person_id)
        serializer = PersonSerializer(person, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, project_id, person_id):
        get_object_or_404(Collaborator, user=request.user, project=request.auth)
        project = request.auth
        person = get_object_or_404(Person, project=project, pk=person_id)

        match = Person.objects.filter(project=project, username=request.data.get('username', None))
        if match.exists() and match[0].pk != person.pk:
            return Response({'message': "This username is taken."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PersonSerializer(person, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, project_id, person_id):
        get_object_or_404(Collaborator, user=request.user, project=request.auth)
        project = request.auth
        person = get_object_or_404(Person, project=project, pk=person_id)
        person_json = PersonSerializer(person, many=False).data
        person.delete()
        return Response(person_json, status=status.HTTP_200_OK)


class ChatsWeb(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenProjectAuthentication,)

    def get_param(self, request, param, default: int = 0):
        try:
            return int(request.GET.get(param, default))
        except TypeError:
            return 0

    def get(self, request, project_id):
        page = self.get_param(request=request, param='page', default=0)
        page_size = self.get_param(request=request, param='page_size', default=250)
        start = page * page_size
        end = (page * page_size) + page_size
        get_object_or_404(Collaborator, user=request.user, project=request.auth)
        project = request.auth
        chats = Chat.objects.filter(project=project)[start:end]
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, project_id):
        get_object_or_404(Collaborator, user=request.user, project=request.auth)
        project = request.auth
        admin_username = request.data.get('admin_username', None)
        person = None if admin_username is None else get_object_or_404(Person, project=project, username=admin_username)
        serializer = ChatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project=project, admin=person)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatDetailsWeb(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenProjectAuthentication,)

    def get(self, request, project_id, chat_id):
        get_object_or_404(Collaborator, user=request.user, project=request.auth)
        project = request.auth
        chat = get_object_or_404(Chat, project=project, pk=chat_id)
        serializer = ChatSerializer(chat, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, project_id, chat_id):
        get_object_or_404(Collaborator, user=request.user, project=request.auth)
        project = request.auth
        chat = get_object_or_404(Chat, project=project, pk=chat_id)

        admin = chat.admin
        admin_username = request.data.get('admin_username', False)
        if admin_username is None:
            admin = None
        elif admin_username:
            admin = get_object_or_404(
                Person, project=project, username=request.data['admin_username'])

        serializer = ChatSerializer(chat, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(admin=admin)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, project_id, chat_id):
        # Get the chat
        get_object_or_404(Collaborator, user=request.user, project=request.auth)
        project = request.auth
        chat = get_object_or_404(Chat, project=project, pk=chat_id)
        new_chat_people = request.data.get('people', [])

        # Get or create list of new chat people (Add first to minimize writes to DB)
        user_names = []
        for new_person in new_chat_people:
            try:
                user_name = new_person.get('person', None)
                person = Person.objects.get(project=project, username=user_name)
                ChatPerson.objects.get_or_create(chat=chat, person=person)
                user_names.append(user_name)

            except Exception as e:
                return Response({'message': 'bad data'}, status=status.HTTP_400_BAD_REQUEST)

        # Delete the users no longer in the list
        for current_chat_person in ChatPerson.objects.filter(chat=chat):
            if current_chat_person.person.username not in user_names:
                current_chat_person.delete()

        # Publish and return new data
        serializer = ChatSerializer(chat, many=False)
        # todo: Implement this
        # chat_publisher.publish_chat_data('edit_chat', serializer.data)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, project_id, chat_id):
        get_object_or_404(Collaborator, user=request.user, project=request.auth)
        project = request.auth
        chat = get_object_or_404(Chat, project=project, pk=chat_id)
        chat_json = ChatSerializer(chat, many=False).data
        chat.delete()
        return Response(chat_json, status=status.HTTP_200_OK)
