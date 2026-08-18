from rest_framework import serializers


class AiHeatingPlanModifyInputSerializer(serializers.Serializer):
    instruction = serializers.CharField(min_length=1, max_length=500)
    plan = serializers.DictField()


class DuplicationExchangeSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["user", "assistant"])
    content = serializers.CharField()


class AiDuplicationDataSerializer(serializers.Serializer):
    """
    Echoed back to the front for display/traceability only. Never trusted as-is on the
    "validate" step — the backend always re-runs validate_ai_duplication_request before
    executing anything, since the front could tamper with these values.
    """

    room_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)
    weekdays = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)
    start = serializers.DateField(allow_null=True, required=False)
    end = serializers.DateField(allow_null=True, required=False)


class AiHeatingPlanDuplicateInputSerializer(serializers.Serializer):
    echanges = serializers.ListField(
        child=DuplicationExchangeSerializer(), min_length=1
    )
    step = serializers.ChoiceField(choices=["clarify", "to_validate", "validate"])
    source_date = serializers.DateField()
    data = AiDuplicationDataSerializer(required=False)
