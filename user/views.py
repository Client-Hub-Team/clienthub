# -*- coding:utf-8 -*-
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from serializers import UserSerializer
from serializers import DataSerializer
from models import Data
from practice.models import Practice
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
                    access_level=data.get('acess_level')
                )

                return Response({'message': 'User created successfully', 'user': user.data, 'data': DataSerializer(userdata).data}, status.HTTP_201_CREATED)
            except Exception as e:
                saved_user.delete()
                return Response({'message': 'User couldnt be created'})

        return Response({'message': 'User could not be created'})


class AddAccountToPractice(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        """
        Adds an existing account to a practice
        :param request:
            {
                "user_id": integer,
                "practice_id": integer
            }
        :return: {message: string}
        """

        data = json.loads(request.body)

        try:
            data = Data.objects.get(user__id=data.get('user_id'))
            data.practice = Practice.objects.get(id='practice_id')
            data.save()

            return Response({'message': 'Practice added to account successfully'}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Practice could not be added'})


