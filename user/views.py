# -*- coding:utf-8 -*-
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from serializers import UserSerializer, DataSerializer, InviteSerializer
from models import Data, Invite, ClientManagement
from practice.models import Practice
from email_helper import Email_Helper
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
                "access_level": integer
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
                    practice_id=data.get('practice_id')
                )

                return Response({'message': 'User created successfully', 'user': user.data, 'data': DataSerializer(userdata).data}, status.HTTP_201_CREATED)
            except Exception as e:
                saved_user.delete()
                return Response({'message': 'User couldnt be created'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'User could not be created'})


class JoinPractice(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        """
        Adds an existing account to a practice, as an Accountant or Client / Admin or Regular
        :param request:
            {
                "user_id": integer,
                "practice_id": integer,
                "user_type": integer,
                "access_level": integer
            }
        :return: {message: string}
        """

        data = json.loads(request.body)

        try:
            data = Data.objects.get(user__id=data.get('user_id'))
            data.practice = Practice.objects.get(id='practice_id')
            data.access_level = data.get('access_level', data.access_level)
            data.user_type = data.get('user_type', data.user_type)
            data.save()

            return Response({'message': 'Account successfully joined company'}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Account couldnt join company'})



class AddClientToAccountant(APIView):

    permission_classes = [AllowAny]

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

            management = ClientManagement.objects.create(accountant=data_accountant, client=data_client)

            return Response({'message': 'Accountant is now managing user'}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Accountant couldnt manage user'})


class InviteClient(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        """
        Invites an user to your CloudClientHub company
        by sending an email to them
        :param request:
            {
                "name": string,
                "email": string,
                "type": integer,
                "invited_by": integer,
            }
        :return: {message: string}
        """

        data = json.loads(request.body)

        try:
            invite = Invite.objects.create(
                email=data.get('email'),
                name=data.get('name'),
                invited_by_id=data.get('invited_by', None),
                type=data.get('type')
            )

            Email_Helper.send(
                to=invite.email,
                subject='Welcome to Client Hub',
                html='<html><head></head><body>Testing</body></html>',
                text=None,
                message_from='welcome@clienthub.com'
            )

            return Response({'message': 'User invited successfully'}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Invite not sent'})


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

            return Response({'invites': InviteSerializer(invites).data}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Invite not sent'})


