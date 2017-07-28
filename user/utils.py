from serializers import UserSerializer, DataSerializer
from models import Data
from practice.models import Practice
from practice.serializers import PracticeSerializer

def jwt_response_payload_handler(token, user=None, request=None):
    try:
        data = Data.objects.get(user_id=user.id)
        serialized_practice = None
        if data.practice is not None:
            practice = Practice.objects.get(id=data.practice.id)
            serialized_practice = PracticeSerializer(practice).data

        return {
            'access_token': token,
            'user': UserSerializer(user).data,
            'data': DataSerializer(data).data,
            'practice': serialized_practice
        }
    except Exception as e:
        return None