from models import Data, Invite
from company.serializers import CompanySerializer
from company.models import Company
from rest_framework import serializers
from django.contrib.auth.models import User
from apps.models import App, UserHasApp
from apps.serializers import AppSerializer


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


class DataSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Data


class AccountantClientSerializer(serializers.ModelSerializer):

    data = serializers.SerializerMethodField()
    apps = serializers.SerializerMethodField()

    class Meta:
        model = User

    def get_data(self, obj):
        data = Data.objects.get(user=obj)
        return DataSimpleSerializer(data).data

    def get_apps(self, obj):
        apps = App.objects.filter(userhasapp__user=obj)
        serialized_apps = AppSerializer(apps, many=True).data

        for app in serialized_apps:
            user_has_app = UserHasApp.objects.get(user_id=obj.id, app_id=app.get('id'))
            app['order'] = user_has_app.order
            app['user_app_id'] = user_has_app.id


        from operator import itemgetter
        sorted_list = sorted(serialized_apps, key=itemgetter('order'))

        return sorted_list


class DataSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    clients = serializers.SerializerMethodField()

    class Meta:
        model = Data

    def get_user(self, obj):
        return UserSerializer(obj.user).data

    def get_clients(self, obj):
        if obj.user_type == Data.CLIENT:
            return None
        return None


class InviteSerializer(serializers.ModelSerializer):
    invited_by = serializers.SerializerMethodField()
    invited_to = serializers.SerializerMethodField()

    class Meta:
        model = Invite

    def get_invited_by(self, obj):
        return UserSerializer(obj.invited_by).data

    def get_invited_to(self, obj):
        if obj.invited_to is None:
            return None
        return CompanySerializer(obj.invited_to).data



