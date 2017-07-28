from models import Data
from rest_framework import serializers
from django.contrib.auth.models import User

class DataSerializer(serializers.ModelSerializer):

     class Meta:
        model = Data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','password', 'username', 'email', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}, }

    # Important note: I changed the validation to user email instead of username, so username is basically
    # useless here. Keep that in mind, ALWAYS.
    def to_internal_value(self, data):
        internal_value = super(UserSerializer, self).to_internal_value(data)
        username = data.get("email")
        password = data.get("password")
        email = data.get("email")
        first_name = data.get("first_name")
        last_name = data.get("last_name")

        internal_value.update({
            "username": username,
            "password": password,
            "email": email,
            "first_name": first_name,
            "last_name": last_name
        })
        return internal_value

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
            return super(UserSerializer, self).update(instance, validated_data)

