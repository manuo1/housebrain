import logging
from datetime import date

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ai.api.serializers import (
    AiEquipmentPlanDuplicateInputSerializer,
    AiEquipmentPlanModifyInputSerializer,
    AiHeatingPlanDuplicateInputSerializer,
    AiHeatingPlanModifyInputSerializer,
)
from ai.services.duplication_interpreter import (
    interpret_duplication_instruction,
    interpret_equipment_duplication_instruction,
)
from ai.services.plan_modifier import modify_equipment_plan, modify_heating_plan
from heating.api.mutators import duplicate_heating_plan_with_override
from heating.api.selectors import get_daily_heating_plan, get_room_heating_day_plan_data
from heating.api.services import (
    build_ai_duplication_recap,
    validate_ai_duplication_request,
)
from planning.api.mutators import duplicate_equipment_plan_with_override
from planning.api.selectors import (
    get_equipment_day_plan_data,
    get_equipment_day_plans,
    get_schedulable_equipment_config,
)
from planning.api.services import (
    build_ai_equipment_duplication_recap,
    make_equipment_key,
    parse_equipment_key,
    validate_ai_equipment_duplication_request,
)
from planning.api.views import SCHEDULABLE_EQUIPMENTS
from planning.services import generate_duplication_dates

logger = logging.getLogger("django")

# Above this many exchanges without reaching "to_validate", give up rather than keep
# looping the LLM — see project notes: ~2 messages per round trip, a handful of rounds
# is normal, beyond that the instruction is probably too ambiguous to resolve.
MAX_EXCHANGES_BEFORE_GIVING_UP = 10


class AiHeatingPlanModifyView(APIView):
    def post(self, request):
        serializer = AiHeatingPlanModifyInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        modified_plan = modify_heating_plan(
            instruction=params["instruction"],
            plan=params["plan"],
        )

        return Response(modified_plan, status=status.HTTP_200_OK)


class AiEquipmentPlanModifyView(APIView):
    def post(self, request):
        serializer = AiEquipmentPlanModifyInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        modified_plan = modify_equipment_plan(
            instruction=params["instruction"],
            plan=params["plan"],
        )

        return Response(modified_plan, status=status.HTTP_200_OK)


def _get_known_room_ids(source_date: date) -> set[int]:
    return {room["room_id"] for room in get_daily_heating_plan(source_date)}


def _give_up_response(echanges: list[dict], source_date: date) -> dict:
    echanges = echanges + [
        {
            "role": "assistant",
            "content": (
                "Je n'arrive pas à traiter votre demande. "
                "Merci de recommencer votre demande depuis le début."
            ),
        }
    ]
    return {
        "echanges": echanges,
        "step": "error",
        "source_date": source_date,
        "data": {"room_ids": [], "weekdays": [], "start": None, "end": None},
    }


class AiHeatingPlanDuplicateView(APIView):
    def post(self, request):
        input_serializer = AiHeatingPlanDuplicateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        params = input_serializer.validated_data

        echanges = params["echanges"]
        step = params["step"]
        source_date = params["source_date"]
        today = timezone.localdate()
        known_room_ids = _get_known_room_ids(source_date)

        if step == "validate":
            data = params.get("data") or {}
            validation = validate_ai_duplication_request(
                data.get("room_ids", []),
                data.get("weekdays", []),
                data["start"].isoformat() if data.get("start") else "",
                data["end"].isoformat() if data.get("end") else "",
                known_room_ids,
                today,
            )
            if validation["status"] == "error":
                echanges = echanges + [
                    {"role": "assistant", "content": validation["message"]}
                ]
                return Response(
                    {
                        "echanges": echanges,
                        "step": "clarify",
                        "source_date": source_date,
                        "data": data,
                    },
                    status=status.HTTP_200_OK,
                )

            created_updated = 0
            duplication_dates = generate_duplication_dates(
                data["start"], data["weekdays"], data["end"]
            )
            for room_id, heating_pattern_id in get_room_heating_day_plan_data(
                source_date, set(data["room_ids"])
            ):
                created_updated += duplicate_heating_plan_with_override(
                    room_id, heating_pattern_id, duplication_dates
                )

            return Response(
                {"status": "validated", "created_updated": created_updated},
                status=status.HTTP_200_OK,
            )

        # step == "clarify": (re)run the LLM interpreter over the full exchange history
        if len(echanges) >= MAX_EXCHANGES_BEFORE_GIVING_UP:
            return Response(
                _give_up_response(echanges, source_date), status=status.HTTP_200_OK
            )

        conversation = [{"role": e["role"], "content": e["content"]} for e in echanges]
        interpretation = interpret_duplication_instruction(
            conversation, source_date, today
        )

        if interpretation["status"] != "ready":
            echanges = echanges + [
                {"role": "assistant", "content": interpretation["message"]}
            ]
            return Response(
                {
                    "echanges": echanges,
                    "step": "clarify",
                    "source_date": source_date,
                    "data": {
                        "room_ids": interpretation.get("room_ids") or [],
                        "weekdays": interpretation.get("weekdays") or [],
                        "start": interpretation.get("start") or None,
                        "end": interpretation.get("end") or None,
                    },
                },
                status=status.HTTP_200_OK,
            )

        validation = validate_ai_duplication_request(
            interpretation["room_ids"],
            interpretation["weekdays"],
            interpretation["start"],
            interpretation["end"],
            known_room_ids,
            today,
        )

        if validation["status"] == "error":
            echanges = echanges + [
                {"role": "assistant", "content": validation["message"]}
            ]
            return Response(
                {
                    "echanges": echanges,
                    "step": "clarify",
                    "source_date": source_date,
                    "data": {
                        "room_ids": interpretation["room_ids"],
                        "weekdays": interpretation["weekdays"],
                        "start": interpretation["start"],
                        "end": interpretation["end"],
                    },
                },
                status=status.HTTP_200_OK,
            )

        start_date = date.fromisoformat(interpretation["start"])
        end_date = date.fromisoformat(interpretation["end"])
        recap = build_ai_duplication_recap(
            source_date,
            interpretation["room_ids"],
            interpretation["weekdays"],
            start_date,
            end_date,
            known_room_ids,
        )
        if validation["status"] == "warning":
            recap += f" {validation['message']}"

        echanges = echanges + [{"role": "assistant", "content": recap}]

        return Response(
            {
                "echanges": echanges,
                "step": "to_validate",
                "source_date": source_date,
                "data": {
                    "room_ids": interpretation["room_ids"],
                    "weekdays": interpretation["weekdays"],
                    "start": start_date,
                    "end": end_date,
                },
            },
            status=status.HTTP_200_OK,
        )


def _get_equipment_names_by_key(source_date: date) -> dict[str, str]:
    # Every equipment is a valid target, with or without a plan on source_date
    # (one without a plan is duplicated as an empty day).
    return {
        make_equipment_key(equipment["type"], equipment["id"]): equipment["name"]
        for equipment in get_equipment_day_plans(SCHEDULABLE_EQUIPMENTS, source_date)
    }


def _give_up_equipment_response(echanges: list[dict], source_date: date) -> dict:
    response = _give_up_response(echanges, source_date)
    response["data"] = {
        "equipment_keys": [],
        "weekdays": [],
        "start": None,
        "end": None,
    }
    return response


class AiEquipmentPlanDuplicateView(APIView):
    def post(self, request):
        input_serializer = AiEquipmentPlanDuplicateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        params = input_serializer.validated_data

        echanges = params["echanges"]
        step = params["step"]
        source_date = params["source_date"]
        today = timezone.localdate()
        equipment_names_by_key = _get_equipment_names_by_key(source_date)
        known_equipment_keys = set(equipment_names_by_key)

        if step == "validate":
            data = params.get("data") or {}
            validation = validate_ai_equipment_duplication_request(
                data.get("equipment_keys", []),
                data.get("weekdays", []),
                data["start"].isoformat() if data.get("start") else "",
                data["end"].isoformat() if data.get("end") else "",
                known_equipment_keys,
                today,
            )
            if validation["status"] == "error":
                echanges = echanges + [
                    {"role": "assistant", "content": validation["message"]}
                ]
                return Response(
                    {
                        "echanges": echanges,
                        "step": "clarify",
                        "source_date": source_date,
                        "data": data,
                    },
                    status=status.HTTP_200_OK,
                )

            created_updated = 0
            duplication_dates = generate_duplication_dates(
                data["start"], data["weekdays"], data["end"]
            )
            # validate_ai_equipment_duplication_request guarantees every key is one of
            # known_equipment_keys, i.e. built by make_equipment_key, so parsing can't fail.
            refs = {parse_equipment_key(key) for key in data["equipment_keys"]}
            for type_name, equipment_id, schedule_pattern_id in get_equipment_day_plan_data(
                SCHEDULABLE_EQUIPMENTS, source_date, refs
            ):
                created_updated += duplicate_equipment_plan_with_override(
                    get_schedulable_equipment_config(
                        SCHEDULABLE_EQUIPMENTS, type_name
                    ),
                    equipment_id,
                    schedule_pattern_id,
                    duplication_dates,
                )

            return Response(
                {"status": "validated", "created_updated": created_updated},
                status=status.HTTP_200_OK,
            )

        # step == "clarify": (re)run the LLM interpreter over the full exchange history
        if len(echanges) >= MAX_EXCHANGES_BEFORE_GIVING_UP:
            return Response(
                _give_up_equipment_response(echanges, source_date),
                status=status.HTTP_200_OK,
            )

        conversation = [{"role": e["role"], "content": e["content"]} for e in echanges]
        interpretation = interpret_equipment_duplication_instruction(
            conversation,
            today,
            [
                {"key": key, "name": name}
                for key, name in equipment_names_by_key.items()
            ],
        )

        if interpretation["status"] != "ready":
            echanges = echanges + [
                {"role": "assistant", "content": interpretation["message"]}
            ]
            return Response(
                {
                    "echanges": echanges,
                    "step": "clarify",
                    "source_date": source_date,
                    "data": {
                        "equipment_keys": interpretation.get("equipment_keys") or [],
                        "weekdays": interpretation.get("weekdays") or [],
                        "start": interpretation.get("start") or None,
                        "end": interpretation.get("end") or None,
                    },
                },
                status=status.HTTP_200_OK,
            )

        validation = validate_ai_equipment_duplication_request(
            interpretation["equipment_keys"],
            interpretation["weekdays"],
            interpretation["start"],
            interpretation["end"],
            known_equipment_keys,
            today,
        )

        if validation["status"] == "error":
            echanges = echanges + [
                {"role": "assistant", "content": validation["message"]}
            ]
            return Response(
                {
                    "echanges": echanges,
                    "step": "clarify",
                    "source_date": source_date,
                    "data": {
                        "equipment_keys": interpretation["equipment_keys"],
                        "weekdays": interpretation["weekdays"],
                        "start": interpretation["start"],
                        "end": interpretation["end"],
                    },
                },
                status=status.HTTP_200_OK,
            )

        start_date = date.fromisoformat(interpretation["start"])
        end_date = date.fromisoformat(interpretation["end"])
        recap = build_ai_equipment_duplication_recap(
            source_date,
            interpretation["equipment_keys"],
            interpretation["weekdays"],
            start_date,
            end_date,
            equipment_names_by_key,
        )
        if validation["status"] == "warning":
            recap += f" {validation['message']}"

        echanges = echanges + [{"role": "assistant", "content": recap}]

        return Response(
            {
                "echanges": echanges,
                "step": "to_validate",
                "source_date": source_date,
                "data": {
                    "equipment_keys": interpretation["equipment_keys"],
                    "weekdays": interpretation["weekdays"],
                    "start": start_date,
                    "end": end_date,
                },
            },
            status=status.HTTP_200_OK,
        )
