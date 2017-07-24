from serializers import UserSerializer, DataSerializer
from models import Data
from practice.models import Practice
from practice.serializers import PracticeSerializer

def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': UserSerializer(user).data,
        'data': DataSerializer(Data.objects.get(user_id=user.id)).data
    }