# -*- coding:utf-8 -*-
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from api.settings import BASE_DIR
from PIL import Image
from rest_framework.parsers import FileUploadParser, MultiPartParser
from models import Resource, UserHasResource, CompanyHasResource
from user.models import Data
from serializers import ResourceSerializer
import cloudinary.uploader
import cloudinary.api
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from user.upload_helper import Upload_Helper
import json
import boto3
import os



class ResourcesAPI(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request):

        """
        Creates a new Resource
        :param request:
            {
                "name": "string",
                "url": "string",
                "logo": "string",
                "category": "string"
            }
        :return: {message: string, app: AppSerializer}
        """
        data = request.data
        file = request.data.get('file')

        try:

            if (file):
                url = Upload_Helper.upload_s3(file=file, file_type=data.get('file_type'), thumb=False)
            else:
                url = data.get('url')

            resource = Resource.objects.create(
                name=data.get('name', ''),
                category=data.get('category'),
                file_type=data.get('file_type'),
                description=data.get('description'),
                url=url,
                company_id=data.get('company_id', None)
            )

            return Response({'resource': ResourceSerializer(resource).data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': 'Error adding new App'}, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request):

        """
        Get all Accounting Company Resources
        :return: {message: string, apps: ResourceSerializer}
        """

        try:
            all_resources = []
            company_resources = []
            accounting_resources = []

            if request.user.data.user_type == Data.ACCOUNTANT:
                all_resources = ResourceSerializer(Resource.objects.filter(company=None), many=True).data
                all_resources += ResourceSerializer(
                    Resource.objects.filter(company=request.user.data.company), many=True
                ).data

            if request.user.data.user_type == Data.CLIENT:
                company_resources = ResourceSerializer(Resource.objects.filter(
                    id__in=CompanyHasResource.objects.filter(company=request.user.data.company)
                        .values_list('resource_id', flat=True)), many=True
                ).data

                for resource in company_resources:
                    company_has_resource = CompanyHasResource.objects.get(
                        company=request.user.data.company,
                        resource_id=resource.get('id')
                    )
                    resource['order'] = company_has_resource.order
                    resource['user_resource_id'] = company_has_resource.id

                from operator import itemgetter
                company_resources = sorted(company_resources, key=itemgetter('order'))

            return Response(
                {
                    'all_resources': all_resources,
                    'company_resources': company_resources,
                    'accounting_resources': accounting_resources
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error retrieving resources'}, status=status.HTTP_400_BAD_REQUEST)









