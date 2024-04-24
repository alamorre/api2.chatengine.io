from server.settings import stripe
from projects.models import Project

hundred_subs = stripe.Subscription.list(limit=100, starting_after='sub_...').data

trial = 'trialing'
active = 'active'
past_due = 'past_due'

def activate_project(subscription_id):
    try:
        project = Project.objects.get(subscription_id=subscription_id)
        if not project.is_active:
            print('was not active...')
            project.is_active = True
            project.save()
    except Project.DoesNotExist:
        print('Active project not found: {}'.format(subscription_id))

def print_project(subscription_id):
    try:
        project = Project.objects.get(subscription_id=subscription_id)
        print(str(project.owner))
    except Project.DoesNotExist:
        print('Project not found: {}'.format(subscription_id))

def deactivate_project(subscription_id):
    try:
        project = Project.objects.get(subscription_id=subscription_id)
        if project.is_active:
            print('should not be active')
            project.is_active = False
            project.save()
    except Project.DoesNotExist:
        print('Past Due project not found: {}'.format(subscription_id))



for i in range(len(hundred_subs)):
    if hundred_subs[i]['status'] == active:
        activate_project(subscription_id=hundred_subs[i]['id'])
    
    if hundred_subs[i]['status'] == past_due:
        print('deactivating {}'.format(hundred_subs[i]['id']))
        deactivate_project(subscription_id=hundred_subs[i]['id'])
