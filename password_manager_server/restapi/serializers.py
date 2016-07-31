from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.conf import settings
from utils import validate_activation_code, authenticate
from authentication import TokenAuthentication
import uuid

try:
    from django.utils.http import urlsafe_base64_decode as uid_decoder
except:
    # make compatible with django 1.5
    from django.utils.http import base36_to_int as uid_decoder

from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers, exceptions
from models import User, Token
import nacl.utils
from nacl.exceptions import CryptoError
import nacl.secret


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    authkey = serializers.CharField(style={'input_type': 'password'},  required=True)
    public_key = serializers.CharField(required=True)

    def validate(self, attrs):
        email = attrs.get('email').lower().strip()
        authkey = attrs.get('authkey')
        public_key = attrs.get('public_key')

        if email and authkey:
            user = authenticate(email=email, authkey=authkey)
        else:
            msg = _('Must include "email" and "authkey".')
            raise exceptions.ValidationError(msg)

        if not user:
            msg = _('Password or e-mail wrong.')
            raise exceptions.ValidationError(msg)

        if len(public_key) != 64:
            msg = _('Session public key seems invalid.')
            raise exceptions.ValidationError(msg)

        if not user.is_active:
            msg = _('User account is disabled.')
            raise exceptions.ValidationError(msg)

        if not user.is_email_active:
            msg = _('E-mail is not yet verified.')
            raise exceptions.ValidationError(msg)

        attrs['user'] = user
        attrs['user_session_public_key'] = public_key
        return attrs

class ActivateTokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    verification = serializers.CharField(required=True)
    verification_nonce = serializers.CharField(required=True)

    def validate(self, attrs):
        verification_hex = attrs.get('verification')
        verification = nacl.encoding.HexEncoder.decode(verification_hex)
        verification_nonce_hex = attrs.get('verification_nonce')
        verification_nonce = nacl.encoding.HexEncoder.decode(verification_nonce_hex)

        token_hash = TokenAuthentication.user_token_to_token_hash(attrs.get('token'))

        try:
            token = Token.objects.filter(key=token_hash, active=False).get()
        except Token.DoesNotExist:
            msg = _('Token incorrect.')
            raise exceptions.ValidationError(msg)

        crypto_box = nacl.secret.SecretBox(token.secret_key, encoder=nacl.encoding.HexEncoder)

        try:
            decrypted = crypto_box.decrypt(verification, verification_nonce)
        except CryptoError:
            msg = _('Verification code incorrect.')
            raise exceptions.ValidationError(msg)


        if token.user_validator != decrypted:
            msg = _('Verification code incorrect.')
            raise exceptions.ValidationError(msg)

        attrs['token'] = token
        return attrs


class VerifyEmailSerializeras(serializers.Serializer):
    activation_code = serializers.CharField(style={'input_type': 'password'}, required=True, )

    def validate(self, attrs):
        activation_code = attrs.get('activation_code').strip()

        if activation_code:
            user = validate_activation_code(activation_code)
        else:
            msg = _('Must include "activation_code".')
            raise exceptions.ValidationError(msg)

        if not user:
            msg = _('Activation code incorrect or already activated.')
            raise exceptions.ValidationError(msg)
        attrs['user'] = user
        attrs['activation_code'] = activation_code
        return attrs


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    authkey = serializers.CharField(style={'input_type': 'password'}, required=True, )

    public_key = serializers.CharField(required=True, )
    private_key = serializers.CharField(required=True, )
    private_key_nonce = serializers.CharField(required=True, )
    secret_key = serializers.CharField(required=True, )
    secret_key_nonce = serializers.CharField(required=True, )
    user_sauce = serializers.CharField(required=True, )

    def validate_email(self, value):

        value = value.lower().strip()

        if User.objects.filter(email=value).exists():
            msg = _('E-Mail already exists.')
            raise exceptions.ValidationError(msg)

        return value

    def validate_authkey(self, value):

        value = value.strip()

        if len(value) < settings.AUTH_KEY_LENGTH_BYTES*2:
            msg = _('Your auth key is too short. It needs to have %s Bytes (%s digits in hex)') % \
                  (str(settings.AUTH_KEY_LENGTH_BYTES), str(settings.AUTH_KEY_LENGTH_BYTES*2), )
            raise exceptions.ValidationError(msg)

        if len(value) > settings.AUTH_KEY_LENGTH_BYTES*2:
            msg = _('Your auth key is too long. It needs to have %s Bytes (%s digits in hex)') % \
                  (str(settings.AUTH_KEY_LENGTH_BYTES), str(settings.AUTH_KEY_LENGTH_BYTES*2), )
            raise exceptions.ValidationError(msg)

        return make_password(value)

    def validate_public_key(self, value):

        value = value.strip()

        if len(value) < settings.USER_PUBLIC_KEY_LENGTH_BYTES*2:
            msg = _('Your public key is too short. It needs to have %s Bytes (%s digits in hex)') % \
                  (str(settings.USER_PUBLIC_KEY_LENGTH_BYTES), str(settings.USER_PUBLIC_KEY_LENGTH_BYTES*2), )
            raise exceptions.ValidationError(msg)

        if len(value) > settings.USER_PUBLIC_KEY_LENGTH_BYTES*2:
            msg = _('Your public key is too long. It needs to have %s Bytes (%s digits in hex)') % \
                  (str(settings.USER_PUBLIC_KEY_LENGTH_BYTES), str(settings.USER_PUBLIC_KEY_LENGTH_BYTES*2), )
            raise exceptions.ValidationError(msg)

        return value

    def validate_private_key(self, value):

        value = value.strip()

        if len(value) < settings.USER_PRIVATE_KEY_LENGTH_BYTES*2:
            msg = _('Your private key is too short. It needs to have %s Bytes (%s digits in hex)') % \
                  (str(settings.USER_PRIVATE_KEY_LENGTH_BYTES), str(settings.USER_PRIVATE_KEY_LENGTH_BYTES*2), )
            raise exceptions.ValidationError(msg)

        if len(value) > settings.USER_PRIVATE_KEY_LENGTH_BYTES*2:
            msg = _('Your private key is too long. It needs to have %s Bytes (%s digits in hex)') % \
                  (str(settings.USER_PRIVATE_KEY_LENGTH_BYTES), str(settings.USER_PRIVATE_KEY_LENGTH_BYTES*2), )
            raise exceptions.ValidationError(msg)

        return value

    def validate_secret_key(self, value):

        value = value.strip()

        if len(value) < settings.USER_SECRET_KEY_LENGTH_BYTES*2:
            msg = _('Your secret key is too short. It needs to have %s Bytes (%s digits in hex)') % \
                  (str(settings.USER_SECRET_KEY_LENGTH_BYTES), str(settings.USER_SECRET_KEY_LENGTH_BYTES*2), )
            raise exceptions.ValidationError(msg)

        if len(value) > settings.USER_SECRET_KEY_LENGTH_BYTES*2:
            msg = _('Your secret key is too long. It needs to have %s Bytes (%s digits in hex)') % \
                  (str(settings.USER_SECRET_KEY_LENGTH_BYTES), str(settings.USER_SECRET_KEY_LENGTH_BYTES*2), )
            raise exceptions.ValidationError(msg)

        return value

    def validate_user_sauce(self, value):

        value = value.strip()

        if len(value) < 1:
            msg = _('You forgot to specify a user sauce') % \
                  (str(settings.USER_SECRET_KEY_LENGTH_BYTES), str(settings.USER_SECRET_KEY_LENGTH_BYTES*2), )
            raise exceptions.ValidationError(msg)

        return value

    def create(self, validated_data):
        return User.objects.create(**validated_data)


class PublicUserDetailsSerializer(serializers.Serializer):
    id = serializers.UUIDField(default=uuid.uuid4)


class PublicShareDetailsSerializer(serializers.Serializer):
    id = serializers.UUIDField(default=uuid.uuid4)

class DatastoreSerializer(serializers.Serializer):

    data = serializers.CharField()
    data_nonce = serializers.CharField(max_length=64)
    type = serializers.CharField(max_length=64, default='password')
    description = serializers.CharField(max_length=64, default='default')
    secret_key = serializers.CharField(max_length=256)
    secret_key_nonce = serializers.CharField(max_length=64)


class SecretSerializer(serializers.Serializer):

    data = serializers.CharField()
    data_nonce = serializers.CharField(max_length=64)
    type = serializers.CharField(max_length=64, default='password')


class UserPublicKeySerializer(serializers.Serializer):

    user_id = serializers.UUIDField(default=uuid.uuid4)
    user_email = serializers.EmailField(required=False)


class UserUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    authkey = serializers.CharField(style={'input_type': 'password'}, required=True, )
    authkey_old = serializers.CharField(style={'input_type': 'password'}, required=True, )

    private_key = serializers.CharField(required=True, )
    private_key_nonce = serializers.CharField(required=True, )
    secret_key = serializers.CharField(required=True, )
    secret_key_nonce = serializers.CharField(required=True, )

    def validate_email(self, value):

        value = value.lower().strip()

        if User.objects.filter(email=value).exclude(pk=self.context['request'].user.pk).exists():
            msg = _('E-Mail already exists.')
            raise exceptions.ValidationError(msg)

        return value

    def validate_authkey(self, value):

        value = value.strip()

        if len(value) < settings.AUTH_KEY_LENGTH_BYTES*2:
            msg = _('Your auth key is too short. It needs to have %s Bytes (%s digits in hex)') % \
                  (str(settings.AUTH_KEY_LENGTH_BYTES), str(settings.AUTH_KEY_LENGTH_BYTES*2), )
            raise exceptions.ValidationError(msg)

        if len(value) > settings.AUTH_KEY_LENGTH_BYTES*2:
            msg = _('Your auth key is too long. It needs to have %s Bytes (%s digits in hex)') % \
                  (str(settings.AUTH_KEY_LENGTH_BYTES), str(settings.AUTH_KEY_LENGTH_BYTES*2), )
            raise exceptions.ValidationError(msg)

        return value

    def validate_authkey_old(self, value):

        value = value.strip()

        if len(value) < settings.AUTH_KEY_LENGTH_BYTES*2 or len(value) > settings.AUTH_KEY_LENGTH_BYTES*2:
            msg = _('Your old password was not right.')
            raise exceptions.ValidationError(msg)

        return value

    def validate_private_key(self, value):

        value = value.strip()

        if len(value) < settings.USER_PRIVATE_KEY_LENGTH_BYTES*2:
            msg = _('Your private key is too short. It needs to have %s Bytes (%s digits in hex)') % \
                  (str(settings.USER_PRIVATE_KEY_LENGTH_BYTES), str(settings.USER_PRIVATE_KEY_LENGTH_BYTES*2), )
            raise exceptions.ValidationError(msg)

        if len(value) > settings.USER_PRIVATE_KEY_LENGTH_BYTES*2:
            msg = _('Your private key is too long. It needs to have %s Bytes (%s digits in hex)') % \
                  (str(settings.USER_PRIVATE_KEY_LENGTH_BYTES), str(settings.USER_PRIVATE_KEY_LENGTH_BYTES*2), )
            raise exceptions.ValidationError(msg)

        return value

    def validate_secret_key(self, value):

        value = value.strip()

        if len(value) < settings.USER_SECRET_KEY_LENGTH_BYTES*2:
            msg = _('Your secret key is too short. It needs to have %s Bytes (%s digits in hex)') % \
                  (str(settings.USER_SECRET_KEY_LENGTH_BYTES), str(settings.USER_SECRET_KEY_LENGTH_BYTES*2), )
            raise exceptions.ValidationError(msg)

        if len(value) > settings.USER_SECRET_KEY_LENGTH_BYTES*2:
            msg = _('Your secret key is too long. It needs to have %s Bytes (%s digits in hex)') % \
                  (str(settings.USER_SECRET_KEY_LENGTH_BYTES), str(settings.USER_SECRET_KEY_LENGTH_BYTES*2), )
            raise exceptions.ValidationError(msg)

        return value


class UserShareSerializer(serializers.Serializer):

    id = serializers.UUIDField(default=uuid.uuid4)
    key = serializers.CharField(max_length=256)
    key_nonce = serializers.CharField(max_length=64)
    title = serializers.CharField(max_length=256)
    read = serializers.BooleanField()
    write = serializers.BooleanField()
    grant = serializers.BooleanField()

    user = PublicUserDetailsSerializer()


class UserShareRightSerializer(serializers.Serializer):
    read = serializers.BooleanField()
    write = serializers.BooleanField()
    grant = serializers.BooleanField()

class ShareTreeSerializer(serializers.Serializer):

    id = serializers.UUIDField(default=uuid.uuid4)
    parent_share = PublicShareDetailsSerializer()
    child_share = PublicShareDetailsSerializer()

class CreateShareSerializer(serializers.Serializer):

    id = serializers.UUIDField(default=uuid.uuid4)
    data = serializers.CharField()
    data_nonce = serializers.CharField(max_length=64)
    key = serializers.CharField(max_length=256)
    key_nonce = serializers.CharField(max_length=64)

    def validate(self, attrs):
        data = attrs.get('data')
        data_nonce = attrs.get('data_nonce')

        if not data or not data_nonce:
            msg = _('Must include "data" and "data_nonce".')
            raise exceptions.ValidationError(msg)

        return attrs


class DatastoreOverviewSerializer(serializers.Serializer):

    id = serializers.UUIDField(default=uuid.uuid4)
    type = serializers.CharField(max_length=64, default='password')
    description = serializers.CharField(max_length=64, default='default')


class SecretOverviewSerializer(serializers.Serializer):

    id = serializers.UUIDField(default=uuid.uuid4)


class ShareOverviewSerializer(serializers.Serializer):

    id = serializers.UUIDField(default=uuid.uuid4)
    data = serializers.CharField()
    data_nonce = serializers.CharField(max_length=64)
    user = serializers.UUIDField(default=uuid.uuid4)

