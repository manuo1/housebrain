from rest_framework import serializers


class AiHeatingPlanModifyInputSerializer(serializers.Serializer):
    instruction = serializers.CharField(min_length=1, max_length=500)
    plan = serializers.DictField()
