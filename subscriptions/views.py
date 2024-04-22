import os 
import stripe

from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404

from projects.models import Project
from projects.serializers import ProjectSerializer
from subscriptions.upgrade_email import upgrade_emailer


STRIPE_PRODUCTS = {
    'light': os.getenv('STRIPE_LIGHT_PLAN', None),
    'light_annual': os.getenv('STRIPE_LIGHT_ANNUAL_PLAN', None),
    'production': os.getenv('STRIPE_PRODUCTION_PLAN', None),
    'production_annual': os.getenv('STRIPE_PRODUCTION_ANNUAL_PLAN', None),
    'professional': os.getenv('STRIPE_PROFESSIONAL_PLAN', None),
    'professional_annual': os.getenv('STRIPE_PROFESSIONAL_ANNUAL_PLAN', None)
}


class Subscriptions(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        event = request.data
        # print(event['type'])

        if event and event['type'] == 'checkout.session.completed' and \
            event['data']['object']['metadata']['webhook_secret'] == os.getenv('STRIPE_WEBHOOK_SECRET'):
            # Gather metadata
            project_id = event['data']['object']['metadata']['project_id']
            plan_type = event['data']['object']['metadata']['plan_type']
            subscription_id = event['data']['object']['subscription']
            # Update Project Obj
            project = Project.objects.get(pk=project_id)
            project.is_active = True
            project.plan_type = plan_type
            project.monthly_users = 1000
            project.message_history = 31
            project.subscription_id = subscription_id
            project.save()
            # Notify me
            upgrade_emailer.email_trial_created(project=project)
            # Attach metadata to Subscription Obj
            stripe.Subscription.modify(subscription_id, metadata={"project_id": project_id})

        # Handle Checkout expiry
        # if event and event['type'] == 'checkout.session.expired' and \
        #     event['data']['object']['metadata']['webhook_secret'] == os.getenv('STRIPE_WEBHOOK_SECRET'):
        #     project_id = event['data']['object']['metadata']['project_id']
        #     try:
        #         project = Project.objects.get(pk=project_id)
        #         project.is_active = False
        #         project.save()
        #         upgrade_emailer.email_payment_failed(project=project)
        #     except Project.DoesNotExist:
        #         pass

        # Handle Customer Cancelled subscription
        if event and event['type'] == 'customer.subscription.deleted':
            # Gather metadata
            subscription_id = event['data']['object']['id']
            # Notify me
            upgrade_emailer.email_subscription_deleted(subscription_id=subscription_id)
            # Update Project Obj
            try:
                project = Project.objects.get(subscription_id=subscription_id)
                project.is_active = False
                project.save()
            except Project.DoesNotExist:
                pass

        return Response({}, status=status.HTTP_200_OK)

class CreateSubscription(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    def patch(self, request, project_id):
        plan = request.data.get('plan', False)
        payment_method = request.data.get('payment_method', False)
        project = get_object_or_404(Project, owner=request.user, pk=project_id)

        quantity = 1000
        if request.data.get('quantity', False) and isinstance(request.data.get('quantity', False), int):
            # Add the needed multiplier, if the quantity is under 1000
            quantity = request.data['quantity'] if request.data['quantity'] > 1000 else request.data['quantity'] * 1000

        if not payment_method or not plan:
            return Response(
                {'message': 'You need a payment method and plan!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            customer = stripe.Customer.create(
                payment_method=payment_method,
                email=request.user.email,
                invoice_settings={'default_payment_method': payment_method},
            )
        except stripe.error.CardError as error:
            message = error.message if error.message else 'We cannot process your C.C. please contact support via chat'
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)

        if project.subscription_id is not None:
            stripe.Subscription.delete(project.subscription_id)

        subscription = stripe.Subscription.create(
            customer=customer['id'],
            items=[{
                'plan': STRIPE_PRODUCTS[plan],
                'quantity': quantity
            }],
            expand=['latest_invoice.payment_intent'],
            default_tax_rates=[os.getenv('STRIPE_TAX_RATE', None)],
            promotion_code=os.getenv('STRIPE_ANNUAL_PROMO', None) if 'annual' in plan else None,
            metadata={"project_id": project_id}
        )

        try:
            if subscription['latest_invoice']['payment_intent']['charges']['data'][0]['payment_method_details']['card']['checks']['cvc_check'] != 'pass':
                return Response({'message': "Your C.C. info is incorrect!"}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            pass

        project.subscription_id = subscription['id']
        project.monthly_users = quantity
        project.plan_type = plan
        project.apply_plan = True
        project.is_active = True
        project.save()

        return Response(subscription['latest_invoice']['payment_intent'], status=status.HTTP_200_OK)

    def delete(self, request, project_id):
        project = get_object_or_404(Project, owner=request.user, pk=project_id)

        try:
            stripe.Subscription.delete(project.subscription_id)
        except stripe.error.InvalidRequestError as error:
            print('Delete Subscription Error: ' + str(error))

        project.subscription_id = None
        project.plan_type = 'basic'
        project.save()

        serializer = ProjectSerializer(project, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
