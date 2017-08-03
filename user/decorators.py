from rest_framework.response import Response
from rest_framework import status
from models import Data

def is_accountant(func):
    def func_wrapper(cls, request):
        if request.user.data.user_type == Data.ACCOUNTANT:
            return func(cls, request)
        return Response({'message': 'You dont have permission to access this resource'}, status.HTTP_403_FORBIDDEN)
    return func_wrapper
