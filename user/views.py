# -*- coding:utf-8 -*-
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from serializers import UserSerializer, DataSerializer, InviteSerializer
from models import Data, Invite, ClientManagement
from company.models import Company
from email_helper import Email_Helper
from decorators import is_accountant
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
                "company_id": integer
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
        Adds an existing client to a accountant
        :param request:
            {
                "accountant_id": integer,
                "client_id": integer
            }
        :return: {message: string}
        """

        data = json.loads(request.body)

        try:
            data_accountant = Data.objects.get(user_id=data.get('accountant_id'))
            data_client = Data.objects.get(user_id=data.get('client_id'))

            if data_client.user_type == Data.CLIENT and \
               data_accountant.user_type == Data.ACCOUNTANT and \
               request.user.data.access_level == Data.ADMIN:
                management = ClientManagement.objects.create(accountant=data_accountant, client=data_client)
            else:
                errors = []
                if data_client.user_type != Data.CLIENT:
                    errors.append('Client is not CLIENT')
                if data_accountant.user_type != Data.ACCOUNTANT:
                    errors.append('Accountant is not ACCOUNTANT')
                if request.user.data.access_level != Data.ADMIN:
                    errors.append('Accountant is not an ADMIN')

                return Response({'message': 'Cannot add client to Accountant', 'errors': errors}, status.HTTP_400_BAD_REQUEST)

            return Response({'message': 'Accountant is now managing user'}, status.HTTP_200_OK)
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
            }
        :return: {message: string}
        """

        data = json.loads(request.body)

        try:
            invited_to = data.get('invited_to', None)

            # If type == ACCOUNTANT, Company cannot be None
            if data.get('type') == 1 and request.user.data.user_type == Data.ACCOUNTANT:
                invited_to = request.user.data.company_id

            # If the user inviting someone is a CLIENT, they can only invite people to their company
            if request.user.data.user_type == Data.CLIENT:
                invited_to = request.user.data.company.id
                # If the inviting user is a CLIENT, ADMIN permission is required to invite someone to join
                if request.user.data.access_level != Data.ADMIN:
                    return Response({'message': 'Wrong request.'}, status=status.HTTP_400_BAD_REQUEST)

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
        :return: {DataSerializer}
        """
        if request.user.data.access_level == Data.ADMIN and request.user.data.user_type == Data.ACCOUNTANT:
            clients = Data.objects.filter(
                company__accounting_company=request.user.data.company,
                user_type=Data.CLIENT
            )
        else:
            clients = Data.objects.filter(
                        id__in=ClientManagement.objects.filter(accountant=request.user.data)
                            .values_list('client_id', flat=True),
                        company__accounting_company=request.user.data.company, user_type=Data.CLIENT
            )
        return Response(DataSerializer(clients, many=True).data, status=status.HTTP_200_OK)





