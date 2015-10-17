from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from ..models import (
    Data_Store,
)

from ..app_settings import (
    DatastoreSerializer, DatastoreOverviewSerializer,
)
from rest_framework.exceptions import PermissionDenied

from django.db import IntegrityError
from ..authentication import TokenAuthentication


class DatastoreView(GenericAPIView):

    """
    Check the REST Token and the object permissions and returns
    the datastore if the necessary access rights are granted

    Accept the following POST parameters: datastore_id (optional)
    Return a list of the datastores or the datastore
    """
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated,)
    serializer_class = DatastoreSerializer

    def get(self, request, uuid = None, *args, **kwargs):

        if not uuid:
            try:
                storages = Data_Store.objects.filter(user=request.user)
            except Data_Store.DoesNotExist:
                storages = []

            return Response({'datastores': DatastoreOverviewSerializer(storages, many=True).data},
                status=status.HTTP_200_OK)
        else:
            try:
                datastore = Data_Store.objects.get(pk=uuid)
            except Data_Store.DoesNotExist:
                return Response({"message":"You don't have permission to access or it does not exist.",
                                "resource_id": uuid}, status=status.HTTP_404_NOT_FOUND)

            if not datastore.user == request.user:
                raise PermissionDenied({"message":"You don't have permission to access",
                                "resource_id": datastore.id})

            return Response(self.serializer_class(datastore).data,
                status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        # TODO implement check for more datastores for enterprise users

        #TODO Check if secret_key and nonce exist

        try:
            datastore = Data_Store.objects.create(
                data = str(request.data['data']),
                data_nonce = str(request.data['data_nonce']),
                secret_key = str(request.data['secret_key']),
                secret_key_nonce = str(request.data['secret_key_nonce']),
                user = request.user
            )
        except IntegrityError:
            return Response({"error": "DuplicateNonce", 'message': "Don't use a nonce twice"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"datastore_id": datastore.id}, status=status.HTTP_201_CREATED)

    def post(self, request, uuid = None, *args, **kwargs):

        try:
            datastore = Data_Store.objects.get(pk=uuid)
        except Data_Store.DoesNotExist:
                return Response({"message":"You don't have permission to access or it does not exist.",
                                "resource_id": uuid}, status=status.HTTP_404_NOT_FOUND)


        if not datastore.user == request.user:
            raise PermissionDenied({"message":"You don't have permission to access",
                            "resource_id": datastore.id})

        if 'data' in request.data:
            datastore.data = str(request.data['data'])
        if 'data_nonce' in request.data:
            datastore.data_nonce = str(request.data['data_nonce'])
        if 'secret_key' in request.data:
            datastore.secret_key = str(request.data['secret_key'])
        if 'secret_key_nonce' in request.data:
            datastore.secret_key_nonce = str(request.data['secret_key_nonce'])

        datastore.save()

        return Response({"success": "Data updated."},
                        status=status.HTTP_200_OK)
