from rest_framework import serializers
from models import Company

class CompanySerializer(serializers.ModelSerializer):

    accounting_company = serializers.SerializerMethodField()

    class Meta:
        model = Company


    def get_accounting_company(self, obj):
        if obj.accounting_company:
            return CompanySerializer(obj.accounting_company).data
        return None