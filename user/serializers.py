from models import UserData
from rest_framework import serializers
from django.contrib.auth.models import User

class UserDataSerializer(serializers.ModelSerializer):

     class Meta:
        model = UserData


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','password', 'username', 'email']
        extra_kwargs = {'password': {'write_only': True}, }


    @staticmethod
    def jwt_response_payload_handler(token, user=None, request=None):
        return {
            'token': token,
            'user': UserSerializer(user).data
        }

    # Important note: I changed the validation to user email instead of username, so username is basically
    # useless here. Keep that in mind, ALWAYS.
    def to_internal_value(self, data):
        internal_value = super(UserSerializer, self).to_internal_value(data)
        username = data.get("email")
        password = data.get("password")
        email = data.get("email")

        internal_value.update({
            "username": username,
            "password": password,
            "email": email
        })
        return internal_value

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
            return super(UserSerializer, self).update(instance, validated_data)

