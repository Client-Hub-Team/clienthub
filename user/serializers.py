from models import Data, Invite, ClientManagement
from company.models import Company
from rest_framework import serializers
from django.contrib.auth.models import User
from apps.models import App, UserHasApp, CompanyHasApp
from resources.models import Resource, UserHasResource, CompanyHasResource
from apps.serializers import AppSerializer
from resources.serializers import ResourceSerializer


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

    class Meta:
        model = User

    def get_data(self, obj):
        data = Data.objects.get(user=obj)
        return DataSimpleSerializer(data).data


# Serializer used to return company info in the practice-info screen
class CompanySerializer(serializers.ModelSerializer):

    accounting_company = serializers.SerializerMethodField()
    apps = serializers.SerializerMethodField()
    # resources = serializers.SerializerMethodField()
    accountants = serializers.SerializerMethodField()
    pending_accountants = serializers.SerializerMethodField()

    class Meta:
        model = Company

    def get_accounting_company(self, obj):
        if obj.accounting_company:
            return CompanySerializer(obj.accounting_company).data
        return None

    def get_apps(self, obj):
        apps = App.objects.filter(companyhasapp__company=obj)
        serialized_apps = AppSerializer(apps, many=True).data

        for app in serialized_apps:
            company_has_app = CompanyHasApp.objects.get(company=obj, app_id=app.get('id'))
            app['order'] = company_has_app.order
            app['user_app_id'] = company_has_app.id

        from operator import itemgetter
        sorted_list = sorted(serialized_apps, key=itemgetter('order'))

        return sorted_list



    def get_accountants(self, obj):
        if obj.is_accounting:
            accountants = Data.objects.filter(
                company=obj,
                user_type=Data.ACCOUNTANT
            )
            return DataSerializer(accountants, many=True).data
        return []

    def get_pending_accountants(self, obj):
        if obj.is_accounting:
            pending = Invite.objects.filter(invited_to=obj, accepted=False, type=Data.ACCOUNTANT).values('name', 'email')
            return pending
        return []



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


# Serializer used to managed invites
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


# Serializer for Accountants loading a client company by clicking on it in the client list
class AccountantClientCompanySerializer(serializers.ModelSerializer):

    owner = serializers.SerializerMethodField()
    apps = serializers.SerializerMethodField()
    resources = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()
    pending_invites = serializers.SerializerMethodField()
    accountants = serializers.SerializerMethodField()

    class Meta:
        model = Company

    def get_owner(self, obj):
        try:
            owner = Data.objects.get(user=obj.owner)
            return DataSerializer(owner).data.get('user')
        except Exception as e:
            return None

    def get_apps(self, obj):
        try:
            apps = App.objects.filter(companyhasapp__company=obj)
            serialized_apps = AppSerializer(apps, many=True).data

            for app in serialized_apps:
                company_has_app = CompanyHasApp.objects.get(company=obj, app_id=app.get('id'))
                app['order'] = company_has_app.order
                app['company_app_id'] = company_has_app.id

            from operator import itemgetter
            sorted_list = sorted(serialized_apps, key=itemgetter('order'))

            return sorted_list
        except Exception as e:
            return []

    def get_resources(self, obj):
        try:
            resources = Resource.objects.filter(companyhasresource__company=obj)
            serialized_resources = ResourceSerializer(resources, many=True).data

            for resource in serialized_resources:
                company_has_resource = CompanyHasResource.objects.get(company=obj, resource_id=resource.get('id'))
                resource['order'] = company_has_resource.order
                resource['company_resource_id'] = company_has_resource.id

            from operator import itemgetter
            sorted_list = sorted(serialized_resources, key=itemgetter('order'))

            return sorted_list
        except Exception as e:
            return []

    def get_users(self, obj):
        try:
            users = Data.objects.filter(company=obj)
            users_serialized = DataSerializer(users, many=True).data

            return users_serialized
        except Exception as e:
            return []

    def get_pending_invites(self, obj):
        try:
            invites = Invite.objects.filter(
                invited_to=obj,
                accepted=False
            )

            return InviteSerializer(invites, many=True).data
        except Exception as e:
            return []


    def get_accountants(self, obj):
        try:
            accountants = Data.objects.filter(
                        id__in=ClientManagement.objects.filter(company=obj)
                            .values_list('accountant_id', flat=True))

            return DataSerializer(accountants, many=True).data
        except Exception as e:
            return []









