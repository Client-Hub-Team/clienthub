from rest_framework import serializers
from models import Company
from apps.serializers import AppSerializer
from apps.models import CompanyHasApp, App

class CompanySerializer(serializers.ModelSerializer):

    accounting_company = serializers.SerializerMethodField()
    apps = serializers.SerializerMethodField()

    class Meta:
        model = Company


    def get_accounting_company(self, obj):
        if obj.accounting_company:
            return CompanySerializer(obj.accounting_company).data
        return None


    def get_apps(self, obj):
        apps = App.objects.filter(companyhasapp__company=obj)
        serialized_apps = AppSerializer(apps, many=True).data

        for app in serialized_apps:
            company_has_app = CompanyHasApp.objects.get(company=obj, app_id=app.get('id'))
            app['order'] = company_has_app.order
            app['user_app_id'] = company_has_app.id


        from operator import itemgetter
        sorted_list = sorted(serialized_apps, key=itemgetter('order'))

        return sorted_list


