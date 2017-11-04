from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from ..models import (
    Google_Authenticator, Yubikey_OTP, Recovery_Code
)

from ..app_settings import (
    UserSearchSerializer
)


from ..authentication import TokenAuthentication

# import the logging
from ..utils import log_info
import logging
logger = logging.getLogger(__name__)


class UserSearch(GenericAPIView):

    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSearchSerializer
    allowed_methods = ('POST', 'OPTIONS', 'HEAD')

    def get(self, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def put(self, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, *args, **kwargs):
        """
        Check the REST Token and returns the user's public key. To identify the user either the email or the user_id needs
        to be provided

        Return the user's public key

        :param request:
        :type request:
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return: 200 / 400
        :rtype:
        """

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():

            log_info(logger=logger, request=request, status='HTTP_400_BAD_REQUEST', event='USER_SEARCH_ERROR', errors=serializer.errors)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data.get('user')

        user_details = {
            'id': user.id,
            'public_key': user.public_key,
            'username': user.username
        }

        if user.id == request.user.id:
            user_details['multifactor_auth_enabled'] = Google_Authenticator.objects.filter(user=user).exists() or Yubikey_OTP.objects.filter(user=user).exists()
            user_details['recovery_code_enabled'] = Recovery_Code.objects.filter(user=user).exists()


        log_info(logger=logger, request=request, status='HTTP_200_OK',
                 event='SEARCH_USER_SUCCESS', request_resource=user.id)

        return Response(user_details, status=status.HTTP_200_OK)

    def delete(self, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
