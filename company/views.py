# -*- coding:utf-8 -*-
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db.models import Max
from rest_framework import status
from api.settings import BASE_DIR
from rest_framework.parsers import FileUploadParser, MultiPartParser
from user.serializers import DataSerializer, CompanySerializer
from user.serializers import AccountantClientCompanySerializer, InviteSerializer
from user.models import Data, ClientManagement, Invite
from user.decorators import is_accountant
from models import Company
from apps.serializers import AppSerializer
from apps.models import CompanyHasApp, App
from PIL import Image
from resources.serializers import ResourceSerializer
from resources.models import Resource, CompanyHasResource
import cloudinary.uploader
import cloudinary.api
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

from pathlib import Path
import json
import os


class CompanyAPI(APIView):
    parser_classes = (MultiPartParser,)

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


    def patch(self, request):

        """
        Update a Company
        :param request:
            {
                "name": "string",
                "url": "string",
                "logo": "string",
                "twitter": "string",
            }
        :return: {message: string, Com  pany: CompanySerializer}
        """
        # data = json.loads(request.body)
        data = request.data
        file = request.data.get('file')
        filename = request.user.data.company.logo

        try:
            if (file):
                destination = os.path.join(BASE_DIR, 'uploads')
                if not os.path.isdir(destination):
                    os.mkdir(destination)

                content = ContentFile(file.read())
                filename = file.name
                path = default_storage.save('{0}'.format(filename), content)

                try:
                    im = Image.open('uploads/{0}'.format(path))
                    im.thumbnail((250,50))
                    im.save('uploads/thumb_{0}'.format(file.name), im.format)
                    upload_result = cloudinary.uploader.upload('uploads/thumb_{0}'.format(file.name))
                    filename = upload_result.get('url')
                    default_storage.delete(file.name)
                    default_storage.delete('thumb_{0}'.format(file.name))
                except IOError:
                    print("cannot create thumbnail for {0}".format(file.name))

            company = request.user.data.company
            company.name = data.get('name', '')
            company.twitter = data.get('twitter', '')
            company.facebook = data.get('facebook', '')
            company.linkedin = data.get('linkedin', '')
            company.color = data.get('color', '')
            company.url = data.get('url', '')
            company.logo = filename

            company.save()

            return Response(CompanySerializer(company).data,
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error updating Company info'}, status=status.HTTP_400_BAD_REQUEST)


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



class CompanyResourcesAPI(APIView):
    @is_accountant
    def get(self, request, company_id):
        """
        Get all client resources
        :return: {message: string, apps: AppSerializer}
        """
        try:

            company_resources = ResourceSerializer(App.objects.filter(
                id__in=CompanyHasResource.objects.filter(company_id=company_id).values_list('id', flat=True)), many=True
            ).data

            for c_app in company_resources:
                c_app['order'] = CompanyHasResource.objects.get(company_id=company_id, resource_id=c_app.get('id')).order

            return Response({'resources': company_resources}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error retrieving apps'}, status=status.HTTP_400_BAD_REQUEST)

    @is_accountant
    def post(self, request, company_id):
        """
        Add an App to a Client
        :param request:
            {
                "resource_id": integer,
            }
        :return: {
                    'message': 'string',
                    'order': company_resource.order,
                    'company_resource_id': company_resource.id
                },
        """

        data = json.loads(request.body)

        try:
            last_order = CompanyHasResource.objects.filter(company_id=company_id).aggregate(Max('order')).get('order__max')
            company_resource = CompanyHasResource.objects.create(
                company_id=company_id,
                resource_id=data.get('resource_id'),
                order=last_order + 1 if last_order is not None else 0
            )

            return Response(
                {
                    'message': 'Resource added successfully',
                    'order': company_resource.order,
                    'company_resource_id': company_resource.id
                },
                status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error adding resource'}, status=status.HTTP_400_BAD_REQUEST)

    @is_accountant
    def patch(self, request, company_id):
        """
        Remove an Resource of a Client
        :param request:
            {
                "resource_id": integer,
            }
        :return: {invites: []}
        """

        data = json.loads(request.body)

        try:
            company_resource = CompanyHasResource.objects.get(company_id=company_id, resource_id=data.get('resource_id'))
            company_resource.delete()
            return Response({'message': 'Resource removed successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error removing resource'}, status=status.HTTP_400_BAD_REQUEST)

    @is_accountant
    def put(self, request, company_id):
        """
        Change client Resources order
        :param request:
            {
                "apps": array,
            }
        :return: {message: string}
        """

        data = json.loads(request.body)

        try:
            for resource in data.get('resources', []):
                company_resource = CompanyHasResource.objects.get(id=resource.get('company_resource_id'))
                if company_resource.order != resource.get('order'):
                    company_resource.order = resource.get('order')
                    company_resource.save()

            return Response({'message': 'Resource order updated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error updating resources order'}, status=status.HTTP_400_BAD_REQUEST)
