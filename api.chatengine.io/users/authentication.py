import json
from rest_framework import authentication
from django.contrib.auth.hashers import check_password
from projects.models import Project, Person
from chats.models import Chat
from subscriptions.upgrade_email import upgrade_emailer
from server.redis import redis_cache
from projects.serializers import ProjectSerializer, PersonSerializer

def get_chat_id(request):
    try:
        routes = request.path.split('/')
        if routes[1] == 'chats' and routes[2] != '':
            return int(routes[2])
        return None
    except ValueError:
        return None

def set_cache(cache_key, user, project):
    user_data = PersonSerializer(user).data if user else None
    project_data = ProjectSerializer(project).data if project else None
    cache_value = json.dumps({'user': user_data, 'project': project_data})
    redis_cache.set(cache_key, cache_value, ex=300)  # Cache for 5 minutes

def get_cache(cache_key):
    cached_value = redis_cache.get(cache_key)
    if cached_value:
        cache_data = json.loads(cached_value)
        return cache_data['user'], cache_data['project']
    return False

class UserSecretAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        public_key = request.headers.get('public-key', None)
        public_key = public_key if public_key else request.headers.get('project-id', None)
        private_key = request.headers.get('private-key', None)
        username = request.headers.get('user-name', None)
        secret = request.headers.get('user-secret', None)

        cache_key = f"{public_key}:{private_key}:{username}:{secret}"
        cache_result = get_cache(cache_key)

        if cache_result:
            pass
            # print(f"Cache hit for {cache_key}: {cache_result}")

        try:
            if public_key is not None:
                project = Project.objects.get(public_key=public_key)

                if not project.is_active:
                    upgrade_emailer.email_project_is_inactive(project=project)
                    raise Exception

                user = Person.objects.get(project=project, username=username)
                if not check_password(secret, user.secret):
                    raise Exception(Person.DoesNotExist, '')

                set_cache(cache_key, user, project)
                return user, project

            if private_key is not None:
                project = Project.objects.get(private_key=private_key)

                if not project.is_active:
                    upgrade_emailer.email_project_is_inactive(project=project)
                    raise Exception

                chat_id = get_chat_id(request=request)

                if username is not None:
                    user = Person.objects.get(project=project, username=username)
                    set_cache(cache_key, user, project)
                    return user, project
                elif chat_id is not None:
                    chat = Chat.objects.get(id=chat_id)
                    set_cache(cache_key, chat.admin, project)
                    return chat.admin, project
                else:
                    try:
                        user = Person.objects.filter(project=project)[:1][0]
                        set_cache(cache_key, user, project)
                        return user, project
                    except IndexError:
                        set_cache(cache_key, None, project)
                        return None, project

            return None

        except:
            set_cache(cache_key, None, None)
            return None
