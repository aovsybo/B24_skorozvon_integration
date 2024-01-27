from rest_framework import serializers

from ..models import CallInfo


class CallInfoSerializer(serializers.ModelSerializer):
    organisation_name = serializers.CharField()
    organisation_phone = serializers.CharField()
    comment = serializers.CharField(allow_blank=True)
    call_id = serializers.CharField()
    scenario_id = serializers.CharField()

    class Meta:
        model = CallInfo
        fields = '__all__'
