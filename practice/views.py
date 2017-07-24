# -*- coding:utf-8 -*-
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from user.serializers import DataSerializer
from practice.serializers import PracticeSerializer
from user.models import Data
import json



class PracticeAPI(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        """
        Creates a new Practice
        :param request:
            {
                "name": "string",
                "url": "string",
                "logo": "string",
                "twitter": "string",
            }
        :return: {message: string, practice: PracticeSerializer}
        """
        data = json.loads(request.body)
        practice = PracticeSerializer(data=data)
        try:

            if practice.is_valid():
                saved_practice = practice.save()
                return Response(PracticeSerializer(saved_practice).data, status=status.HTTP_201_CREATED)
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



