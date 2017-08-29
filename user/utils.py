from serializers import UserSerializer, DataSerializer, CompanySerializer
from models import Data
from company.models import Company

def jwt_response_payload_handler(token, user=None, request=None):
    try:
        data = Data.objects.get(user_id=user.id)
        serialized_company = None
        if data.company is not None:
            company = Company.objects.get(id=data.company.id)
            serialized_company = CompanySerializer(company).data

        return {
            'access_token': token,
            'user': UserSerializer(user).data,
            'data': DataSerializer(data).data,
            'company': serialized_company
        }
    except Exception as e:
        return None