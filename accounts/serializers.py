from rest_framework import serializers
from django.contrib.auth.hashers import make_password

# from support.serializers import SupportChatSerializer

from .models import User, Reset


class ResetSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Reset
        fields = '__all__'

class MFASerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    mfa_code = serializers.UUIDField(required=True)


class UserPublicSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField  # Email also has the id field

    class Meta(object):
        model = User
        fields = [
            'email',
        ]


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=False)
    # support_chat = SupportChatSerializer(required=False)
    reset = ResetSerializer(required=False)

    class Meta(object):
        model = User
        fields = ['email', 'password', 'reset'] # TODO: Add support_chat

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(UserSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)

        password = validated_data.get('password', None)
        if password is not None:
            instance.password = make_password(validated_data.get('password'))

        instance.save()
        return instance
