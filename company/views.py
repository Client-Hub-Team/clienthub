# -*- coding:utf-8 -*-
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db.models import Max
from rest_framework import status
from user.serializers import DataSerializer
from company.serializers import CompanySerializer
from user.serializers import AccountantClientCompanySerializer, InviteSerializer
from user.models import Data, ClientManagement, Invite
from user.decorators import is_accountant
from models import Company
from apps.serializers import AppSerializer
from apps.models import CompanyHasApp, App
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
                "accounting_company": integer (optional),
                "invite_id": integer (optional)
            }
        :return: {message: string, Company: CompanySerializer}
        """
        data = json.loads(request.body)

        try:

            data_obj = None

            if data.get('invite_id', None):
                invite = Invite.objects.get(id=data.get('invite_id'))
                data_obj = Data.objects.get(user_id=invite.invited_by.id)

            company = Company.objects.create(
                name=data.get('name'),
                url=data.get('url'),
                logo=data.get('logo'),
                twitter=data.get('twitter'),
                is_accounting=data.get('is_accounting', False),
                owner_id=data.get('owner'),
                accounting_company_id=data_obj.company.id if data_obj is not None else None
            )
            data = Data.objects.get(user=request.user)
            data.company = company
            data.save()

            return Response({'company': CompanySerializer(company).data, 'data': DataSerializer(data).data},
                            status=status.HTTP_201_CREATED)
        except Exception:
            return Response({'message': 'Error adding new Company'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """
        Returns company info
        :return: {CompanySerializer}
        """
        company = Company.objects.get(id=request.user.data.company_id)
        return Response(CompanySerializer(company).data, status=status.HTTP_200_OK)


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
    @is_accountant
    def get(self, request, company_id):
        """
        Returns all Company clients
        :return: {DataSerializer}
        """
        if request.user.data.access_level == Data.ADMIN:
            clients = Data.objects.filter(company=company_id, company__accounting_company=request.user.data.company,
                                          user_type=Data.CLIENT)
        else:
            clients = Data.objects.filter(
                id__in=ClientManagement.objects.filter(
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


class CompanyPendingInvitesAPI(APIView):
    @is_accountant
    def get(self, request, company_id):

        """
        Get company invites for accountant view
        :return: {message: string, company: CompanySerializer}
        """

        try:
            invites = Invite.objects.filter(
                invited_to=company_id,
                accepted=False,
                invited_to__accounting_company=request.user.data.company
            )

            invites_serialized = InviteSerializer(invites).data

            return Response({'invites': invites_serialized}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error retrieving apps'}, status=status.HTTP_400_BAD_REQUEST)


class CompanyInfoAPI(APIView):
    @is_accountant
    def get(self, request, company_id):

        """
        Get company info for accountant view
        :return: {message: string, company: CompanySerializer}
        """

        try:
            company = Company.objects.get(id=company_id)
            company_serialized = AccountantClientCompanySerializer(company).data

            return Response({'company': company_serialized}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error retrieving apps'}, status=status.HTTP_400_BAD_REQUEST)


class CompanyAppsAPI(APIView):
    @is_accountant
    def get(self, request, company_id):
        """
        Get all client apps
        :return: {message: string, apps: AppSerializer}
        """
        try:

            company_apps = AppSerializer(App.objects.filter(
                id__in=CompanyHasApp.objects.filter(company_id=company_id).values_list('id', flat=True)), many=True
            ).data

            for c_app in company_apps:
                c_app['order'] = CompanyHasApp.objects.get(company_id=company_id, app_id=c_app.get('id')).order

            return Response({'apps': company_apps}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error retrieving apps'}, status=status.HTTP_400_BAD_REQUEST)

    @is_accountant
    def post(self, request, company_id):
        """
        Add an App to a Client
        :param request:
            {
                "app_id": integer,
            }
        :return: {invites: []}
        """

        data = json.loads(request.body)

        try:
            last_order = CompanyHasApp.objects.filter(company_id=company_id).aggregate(Max('order')).get('order__max')
            company_app = CompanyHasApp.objects.create(
                company_id=company_id,
                app_id=data.get('app_id'),
                order=last_order + 1 if last_order is not None else 0
            )

            return Response(
                {'message': 'App added successfully', 'order': company_app.order, 'company_app_id': company_app.id},
                status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error retrieving apps'}, status=status.HTTP_400_BAD_REQUEST)

    @is_accountant
    def patch(self, request, company_id):
        """
        Remove an App of a Client
        :param request:
            {
                "app_id": integer,
            }
        :return: {invites: []}
        """

        data = json.loads(request.body)

        try:
            company_app = CompanyHasApp.objects.get(company_id=company_id, app_id=data.get('app_id'))
            company_app.delete()
            return Response({'message': 'App removed successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error retrieving apps'}, status=status.HTTP_400_BAD_REQUEST)

    @is_accountant
    def put(self, request, company_id):
        """
        Change client apps order
        :param request:
            {
                "apps": array,
            }
        :return: {message: string}
        """

        data = json.loads(request.body)

        try:
            for app in data.get('apps', []):
                company_app = CompanyHasApp.objects.get(id=app.get('company_app_id'))
                if company_app.order != app.get('order'):
                    company_app.order = app.get('order')
                    company_app.save()

            return Response({'message': 'App order updated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error updating apps order'}, status=status.HTTP_400_BAD_REQUEST)
