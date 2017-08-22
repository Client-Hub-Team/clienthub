# -*- coding:utf-8 -*-
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from serializers import UserSerializer, DataSerializer, InviteSerializer, AccountantClientSerializer,\
    AccountantClientCompanySerializer
from models import Data, Invite, ClientManagement
from company.models import Company
from apps.serializers import AppSerializer
from apps.models import App, UserHasApp
from email_helper import Email_Helper
from django.contrib.auth.models import User
from decorators import is_accountant
from django.db.models import Max
import json


class AccountAPI(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Creates a new account
        :param request:
            {
                "username": "string",
                "first_name": "string",
                "last_name": "string",
                "password": "string",
                "email": "string",
                "user_type": integer,
                "access_level": integer,
                "company_id": integer,
                "invite_id": integer
            }
        :return: {message: string, user: UserSerializer, data: DataSerializer}
        """

        data = json.loads(request.body)
        user = UserSerializer(data=data)

        if user.is_valid():
            saved_user = user.save()

            try:
                userdata = Data.objects.create(
                    user=saved_user,
                    user_type=data.get('user_type'),
                    access_level=data.get('access_level'),
                    company_id=data.get('company_id')
                )

                # if the user is a Client, test if it is the first one of that company
                # to change ownership

                if data.get('user_type') == Data.CLIENT:
                    company = Company.objects.get(id=data.get('company_id'))
                    if company.owner is None:
                        company.owner = saved_user
                        company.save()

                        userdata.access_level = Data.ADMIN
                        userdata.save()

                if data.get('invite_id', None):
                    invite = Invite.objects.get(id=data.get('invite_id'))
                    invite.accepted = True
                    invite.save()

                return Response({'message': 'User created successfully', 'user': user.data, 'data': DataSerializer(userdata).data}, status.HTTP_201_CREATED)
            except Exception as e:
                saved_user.delete()
                return Response({'message': 'User couldnt be created'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'User could not be created'})


class JoinCompany(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        """
        Adds an existing account to a company, as an Accountant or Client / Admin or Regular
        :param request:
            {
                "user_id": integer,
                "company_id": integer,
                "user_type": integer,
                "access_level": integer
            }
        :return: {message: string}
        """

        data = json.loads(request.body)

        try:
            data = Data.objects.get(user__id=data.get('user_id'))
            data.company = Company.objects.get(id='company_id')
            data.access_level = data.get('access_level', data.access_level)
            data.user_type = data.get('user_type', data.user_type)
            data.save()

            return Response({'message': 'Account successfully joined company'}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Account couldnt join company'})



class AddClientToAccountant(APIView):


    @is_accountant
    def post(self, request):

        """
        Adds an existing client company to a accountant
        :param request:
            {
                "accountant_id": integer,
                "company_id": integer
            }
        :return: {message: string}
        """

        data = json.loads(request.body)

        try:
            data_accountant = Data.objects.get(user_id=data.get('accountant_id'))
            company_client = Company.objects.get(id=data.get('company_id'))

            if company_client.is_accounting == False and \
               data_accountant.user_type == Data.ACCOUNTANT and \
               request.user.data.access_level == Data.ADMIN:
                management = ClientManagement.objects.create(accountant=data_accountant, company=company_client)
            else:
                errors = []
                if data_accountant.user_type != Data.ACCOUNTANT:
                    errors.append('Accountant is not ACCOUNTANT')
                if request.user.data.access_level != Data.ADMIN:
                    errors.append('Accountant is not an ADMIN')

                return Response({'message': 'Cannot add client to Accountant', 'errors': errors}, status.HTTP_400_BAD_REQUEST)

            return Response({'message': 'Accountant is now managing company'}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Accountant couldnt manage user'}, status.HTTP_400_BAD_REQUEST)


class InviteClient(APIView):

    def post(self, request):

        """
        Invites an user to a company
        by sending an email to them
        :param request:
            {
                "name": string,
                "email": string,
                "type": integer,
                "company_name": string
            }
        :return: {message: string}
        """

        data = json.loads(request.body)

        try:
            invited_to = data.get('invited_to', None)

            # If type == ACCOUNTANT, Company cannot be None
            if data.get('type') == Data.ACCOUNTANT and request.user.data.user_type == Data.ACCOUNTANT:
                invited_to = request.user.data.company_id

            # If the user inviting someone is a CLIENT, they can only invite people to their company
            if request.user.data.user_type == Data.CLIENT:
                invited_to = request.user.data.company.id
                # If the inviting user is a CLIENT, ADMIN permission is required to invite someone to join
                if request.user.data.access_level != Data.ADMIN:
                    return Response({'message': 'Wrong request.'}, status=status.HTTP_400_BAD_REQUEST)

            if request.user.data.user_type == Data.ACCOUNTANT and request.data.get('type') == 2:
                if invited_to is None:
                    invited_to = Company.objects.create(
                        name=data.get('company_name'),
                        is_accounting=False,
                        accounting_company=request.user.data.company
                    ).id

            invite = Invite.objects.create(
                email=data.get('email'),
                name=data.get('name'),
                invited_by=request.user,
                invited_to_id=invited_to,
                type=data.get('type')
            )

            # Email_Helper.send(
            #     to=invite.email,
            #     subject='Welcome to Client Hub',
            #     html='<html><head></head><body>Testing</body></html>',
            #     text=None,
            #     message_from='welcome@clienthub.com'
            # )

            return Response({'message': 'User invited successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Invite not sent'}, status=status.HTTP_400_BAD_REQUEST)


class CheckInvitation(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        """
        Check what invitations an email has
        :param request:
            {
                "email": string,
            }
        :return: {invites: []}
        """

        data = json.loads(request.body)

        try:
            invites = Invite.objects.filter(email=data.get('email'))

            return Response({'invites': InviteSerializer(invites, many=True).data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'You dont have any invites', 'invites': []}, status=status.HTTP_400_BAD_REQUEST)


class AccountantClientsAPI(APIView):

    @is_accountant
    def get(self, request):
        """
        Returns all accountant clients
        :return: {AccountantClientSerializerSerializer}
        """
        if request.user.data.access_level == Data.ADMIN and request.user.data.user_type == Data.ACCOUNTANT:
            clients = Company.objects.filter(
                accounting_company=request.user.data.company,
                is_accounting=False
            )
        else:
            clients = Company.objects.filter(
                        id__in=ClientManagement.objects.filter(accountant=request.user.data)
                            .values_list('company_id', flat=True),
                        accounting_company=request.user.data.company, is_accounting=False
            )
        return Response(AccountantClientCompanySerializer(clients, many=True).data, status=status.HTTP_200_OK)




class ClientAppsAPI(APIView):

    @is_accountant
    def get(self, request, user_id):
        """
        Get all client apps
        :return: {message: string, apps: AppSerializer}
        """
        try:


            client_apps = AppSerializer(App.objects.filter(
                id__in=UserHasApp.objects.filter(user_id=user_id).values_list('id', flat=True)), many=True
            ).data

            for c_app in client_apps:
                c_app['order'] = UserHasApp.objects.get(user_id=user_id, app_id=c_app.get('id')).order

            return Response({'apps': client_apps}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error retrieving apps'}, status=status.HTTP_400_BAD_REQUEST)

    @is_accountant
    def post(self, request, user_id):
        """
        Add an App to a Client
        :param request:
            {
                "app_id": integer,
            }
        :return: {invites: []}
        """

        data = json.loads(request.body)

        try:
            last_order = UserHasApp.objects.filter(user_id=user_id).aggregate(Max('order')).get('order__max')
            user_app = UserHasApp.objects.create(
                user_id=user_id,
                app_id=data.get('app_id'),
                order=last_order+1 if last_order is not None else 0
            )

            return Response({'message': 'App added successfully', 'order': user_app.order, 'user_app_id': user_app.id},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error retrieving apps'}, status=status.HTTP_400_BAD_REQUEST)

    @is_accountant
    def patch(self, request, user_id):
        """
        Remove an App of a Client
        :param request:
            {
                "app_id": integer,
            }
        :return: {invites: []}
        """

        data = json.loads(request.body)

        try:
            user_app = UserHasApp.objects.get(user_id=user_id, app_id=data.get('app_id'))
            user_app.delete()
            return Response({'message': 'App removed successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error retrieving apps'}, status=status.HTTP_400_BAD_REQUEST)

    @is_accountant
    def put(self, request, user_id):
        """
        Change client apps order
        :param request:
            {
                "apps": array,
            }
        :return: {message: string}
        """

        data = json.loads(request.body)

        try:
            for app in data.get('apps', []):
                user_app = UserHasApp.objects.get(id=app.get('user_app_id'))
                if user_app.order != app.get('order'):
                    user_app.order = app.get('order')
                    user_app.save()

            return Response({'message': 'App order updated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error updating apps order'}, status=status.HTTP_400_BAD_REQUEST)


class ClientInfoAPI(APIView):

    @is_accountant
    def get(self, request, user_id):

        """
        Get client info for accountant view
        :return: {message: string, client: ClientSerializer}
        """

        try:
            user = User.objects.get(id=user_id)
            user_serialized = AccountantClientSerializer(user).data

            return Response({'client': user_serialized}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error retrieving apps'}, status=status.HTTP_400_BAD_REQUEST)





