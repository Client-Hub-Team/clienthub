# -*- coding:utf-8 -*-


from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from serializers import UserSerializer
from serializers import UserDataSerializer
from models import UserData
from django.contrib.auth.models import User
import json


class AccountAPI(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        data = json.loads(request.body)
        user = UserSerializer(data=data)

        if user.is_valid():
            saved_user = user.save()

            userdata = UserData.objects.create(
                user=saved_user,
                is_practice=data.get('is_practice') if data.get('manager') is None or data.get('manager') == '' else False,
                manager=User.objects.get(id=data.get('manager'))
            )

            return Response({'user': user.data, 'userdata': UserDataSerializer(userdata).data}, status.HTTP_201_CREATED)

        return Response({'message': 'User couldnt be created'})

class UserDataAPI(APIView):

    def post(self, request):
        data = json.loads(request.body)
        try:
            userdata = UserData.objects.get(user=request.user)
            userdata.is_practice=data.get('is_practice')
            userdata.save()

            serializer = UserDataSerializer(userdata)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserData.DoesNotExist:
            return Response({'message': 'UserData does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'message': 'Error adding UserData info'}, status=status.HTTP_400_BAD_REQUEST)



