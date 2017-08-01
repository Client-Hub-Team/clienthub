# -*- coding:utf-8 -*-
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from user.serializers import DataSerializer
from company.serializers import CompanySerializer
from user.models import Data, ClientManagement
from models import Company
import json



class CompanyAPI(APIView):

    def post(self, request):

        """
        Creates a new Company
        :param request:
            {
                "name": "string",
                "url": "string",
                "logo": "string",
                "twitter": "string",
                "is_accounting": "boolean,
                "owner": integer,
                "accounting_company": integer
            }
        :return: {message: string, Company: CompanySerializer}
        """
        data = json.loads(request.body)

        try:
            company = Company.objects.create(
                name=data.get('name'),
                url=data.get('url'),
                logo=data.get('logo'),
                twitter=data.get('twitter'),
                is_accounting=data.get('is_accounting', False),
                owner_id=data.get('owner'),
                accounting_company_id=data.get('accounting_company', None)
            )
            data = Data.objects.get(user=request.user)
            data.company = company
            data.save()

            return Response({'company': CompanySerializer(company).data, 'data': DataSerializer(data).data}, status=status.HTTP_201_CREATED)
        except Exception:
            return Response({'message': 'Error adding new Company'}, status=status.HTTP_400_BAD_REQUEST)


class AddAccountingCompanyToCompanyAPI(APIView):

    def post(self, request):

        """
        Creates a new Company
        :param request:
            {
                "company": integer,
                "accounting_company": integer
            }
        :return: {message: string, Company: CompanySerializer}
        """
        data = json.loads(request.body)

        try:
            company = Company.objects.get(id=data.get('company'))
            company.accounting_company = Company.objects.get(id=data.get('accounting_company'))
            company.save()

            return Response({'company': CompanySerializer(company).data}, status=status.HTTP_201_CREATED)
        except Exception:
            return Response({'message': 'Error adding new Company'}, status=status.HTTP_400_BAD_REQUEST)


class CompanyClientsAPI(APIView):

    def get(self, request):
        """
        Returns all Clients from a Company base on access levels
        :param company_id:
        :return: {DataSerializer}
        """
        if request.user.data.access_level == Data.ADMIN:
            clients = Data.objects.filter(company=request.user.data.company, user_type=Data.CLIENT)
        else:
            clients = Data.objects.filter(
                user_id__in=ClientManagement.objects.filter(
                    accountant=request.user.data).values_list('client_id', flat=True),
                company=request.user.data.company, user_type=Data.CLIENT
            )
        return Response(DataSerializer(clients, many=True).data, status=status.HTTP_200_OK)


class CompanyAccountantsAPI(APIView):

    def get(self, request, company_id):
        """
        Returns all Accountants from a Company
        :param company_id:
        :return: {DataSerializer}
        """
        accountants = Data.objects.filter(company_id=company_id, user_type=Data.ACCOUNTANT)
        return Response(DataSerializer(accountants).data, status=status.HTTP_200_OK)



