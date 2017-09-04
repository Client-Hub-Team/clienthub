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
import json
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

            else:

                filename = data.get('url')

            resource = Resource.objects.create(
                name=data.get('name', ''),
                category=data.get('category'),
                file_type=data.get('file_type'),
                description=data.get('description'),
                url=filename,
                company_id=data.get('company_id', None)
            )

            return Response({'resource': ResourceSerializer(resource).data}, status=status.HTTP_201_CREATED)
        except Exception:
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









