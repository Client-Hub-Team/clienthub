# -*- coding:utf-8 -*-
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from models import Resource, UserHasResource, CompanyHasResource
from user.models import Data
from serializers import ResourceSerializer
import json



class ResourcesAPI(APIView):

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
        data = json.loads(request.body)

        try:

            resource = Resource.objects.create(
                name=data.get('name'),
                category=data.get('category'),
                url=data.get('url'),
                logo=data.get('logo')
            )

            return Response({'resource': ResourceSerializer(resource).data}, status=status.HTTP_201_CREATED)
        except Exception:
            return Response({'message': 'Error adding new App'}, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request):

        """
        Get all Company Resources
        :return: {message: string, apps: ResourceSerializer}
        """

        try:
            all_resources = []
            company_resources = []

            if request.user.data.user_type == Data.ACCOUNTANT:
                all_resources = ResourceSerializer(Resource.objects.filter(company=None), many=True).data

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

            return Response({'all_resources': all_resources, 'company_resources': company_resources}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error retrieving resources'}, status=status.HTTP_400_BAD_REQUEST)









