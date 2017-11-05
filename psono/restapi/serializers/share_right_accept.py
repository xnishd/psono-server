from django.utils.http import urlsafe_base64_decode as uid_decoder

from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers, exceptions

from ..utils import user_has_rights_on_share, get_datastore
from ..models import User_Share_Right

class ShareRightAcceptSerializer(serializers.Serializer):

    share_right_id = serializers.UUIDField(required=True)
    key = serializers.CharField(max_length=256, required=False)
    key_type = serializers.CharField(max_length=256, required=False, default='symmetric')
    key_nonce = serializers.CharField(max_length=64, required=False)

    def validate(self, attrs):
        share_right_id = attrs.get('share_right_id')
        key_type = attrs.get('key_type')

        if key_type not in ['asymmetric', 'symmetric']:
            msg = _("Invalid Key Type")
            raise exceptions.ValidationError(msg)

        try:
            user_share_right_obj = User_Share_Right.objects.get(pk=share_right_id, user=self.context['request'].user, accepted=None)
        except User_Share_Right.DoesNotExist:
            msg = _("You don't have permission to access it or it does not exist or you already accepted or declined this share.")
            raise exceptions.ValidationError(msg)

        attrs['user_share_right_obj'] = user_share_right_obj

        return attrs