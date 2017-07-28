# -*- coding:utf-8 -*-
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from user.serializers import DataSerializer
from practice.serializers import PracticeSerializer
from user.models import Data
from models import Practice
import json



class PracticeAPI(APIView):

    def post(self, request):

        """
        Creates a new Practice
        :param request:
            {
                "name": "string",
                "url": "string",
                "logo": "string",
                "twitter": "string",
                "is_accounting": "boolean,
                "owner": integer
            }
        :return: {message: string, practice: PracticeSerializer}
        """
        data = json.loads(request.body)

        try:
            practice = Practice.objects.create(
                name=data.get('name'),
                url=data.get('url'),
                logo=data.get('logo'),
                twitter=data.get('twitter'),
                is_accounting=data.get('is_accounting', False),
                owner_id=data.get('owner'),
            )
            data = Data.objects.get(user=request.user)
            data.practice = practice
            data.save()

            return Response({'practice': PracticeSerializer(practice).data, 'data': DataSerializer(data).data}, status=status.HTTP_201_CREATED)
        except Exception:
            return Response({'message': 'Error adding new Practice'}, status=status.HTTP_400_BAD_REQUEST)



class PraticeClientsAPI(APIView):

    def get(self, request, practice_id):
        """
        Returns all Clients from a Practice
        :param practice_id:
        :return: {DataSerializer}
        """
        clients = Data.objects.filter(practice_id=practice_id, user_type=Data.CLIENT)
        return Response(DataSerializer(clients).data, status=status.HTTP_200_OK)

class PraticeAccountantsAPI(APIView):

    def get(self, request, practice_id):
        """
        Returns all Accountants from a Practice
        :param practice_id:
        :return: {DataSerializer}
        """
        accountants = Data.objects.filter(practice_id=practice_id, user_type=Data.ACCOUNTANT)
        return Response(DataSerializer(accountants).data, status=status.HTTP_200_OK)

# class PraticeAccountantsAPI(APIView):
#
#     def get(self, request, practice_id):
#         accountants = Data.objects.filter(practice_id=practice_id, user_type=Data.ACCOUNTANT)
#         return Response(DataSerializer(accountants).data, status=status.HTTP_200_OK)



