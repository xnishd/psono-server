from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

from ..models import Yubikey_OTP
from ..app_settings import NewYubikeyOTPSerializer, DeleteYubikeySerializer
from ..authentication import TokenAuthentication
from ..utils import encrypt_with_db_secret


class UserYubikeyOTP(GenericAPIView):

    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated,)
    serializer_class = NewYubikeyOTPSerializer
    allowed_methods = ('GET', 'PUT', 'DELETE', 'OPTIONS', 'HEAD')

    def get(self, request, *args, **kwargs):
        """
        Checks the REST Token and returns a list of a all YubiKey OTPs

        :param request:
        :type request:
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return: 200
        :rtype:
        """

        yubikey_otps = []

        for ga in Yubikey_OTP.objects.filter(user=request.user).all():
            yubikey_otps.append({
                'id': ga.id,
                'title': ga.title,
            })

        return Response({
            "yubikey_otps": yubikey_otps
        },
            status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        """
        Checks the REST Token and sets a new YubiKey OTP for multifactor authentication

        :param request:
        :type request:
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return: 201 / 400
        :rtype:
        """

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        yubikey_otp = serializer.validated_data.get('yubikey_otp')
        yubikey_id = yubikey_otp[:12]

        new_yubikey = Yubikey_OTP.objects.create(
            user=request.user,
            title= serializer.validated_data.get('title'),
            yubikey_id = encrypt_with_db_secret(str(yubikey_id))
        )

        return Response({
            "id": new_yubikey.id,
        },
            status=status.HTTP_201_CREATED)

    def post(self, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request, *args, **kwargs):
        """
        Deletes an Yubikey

        :param request:
        :param args:
        :param kwargs:
        :return: 200 / 400
        """

        serializer = DeleteYubikeySerializer(data=request.data, context=self.get_serializer_context())

        if not serializer.is_valid():

            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        yubikey_otp = serializer.validated_data.get('yubikey_otp')

        # delete it
        yubikey_otp.delete()

        return Response(status=status.HTTP_200_OK)
