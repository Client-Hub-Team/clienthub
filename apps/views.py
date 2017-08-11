# -*- coding:utf-8 -*-
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from models import App, UserHasApp
from user.models import Data
from serializers import AppSerializer
import json



class AppsAPI(APIView):

    def post(self, request):

        """
        Creates a new App
        :param request:
            {
                "name": "string",
                "url": "string",
                "logo": "string",
                "category": "string"
            }
        :return: {message: string, app: AppSerializer}
        """
        data = json.loads(request.body)

        try:

            app = App.objects.create(
                name=data.get('name'),
                category=data.get('category'),
                url=data.get('url'),
                logo=data.get('logo')
            )

            return Response({'app': AppSerializer(app).data}, status=status.HTTP_201_CREATED)
        except Exception:
            return Response({'message': 'Error adding new App'}, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request):

        """
        Get all Apps
        :return: {message: string, apps: AppSerializer}
        """

        try:
            all_apps = []
            client_apps = []

            if request.user.data.user_type == Data.ACCOUNTANT:
                all_apps = AppSerializer(App.objects.all(), many=True).data

            if request.user.data.user_type == Data.CLIENT:
                client_apps = AppSerializer(App.objects.filter(
                    id__in=UserHasApp.objects.filter(user=request.user).values_list('app_id', flat=True)), many=True
                ).data

            return Response({'all_apps': all_apps, 'client_apps': client_apps}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error retrieving apps'}, status=status.HTTP_400_BAD_REQUEST)









