import logging
from datetime import date

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ai.api.serializers import AiHeatingPlanDuplicateInputSerializer, AiHeatingPlanModifyInputSerializer
from ai.services.duplication_interpreter import interpret_duplication_instruction
from ai.services.plan_modifier import modify_heating_plan
from heating.api.mutators import duplicate_heating_plan_with_override
from heating.api.selectors import get_daily_heating_plan, get_room_heating_day_plan_data
from heating.api.services import build_ai_duplication_recap, generate_duplication_dates, validate_ai_duplication_request

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
            return Response(_give_up_response(echanges, source_date), status=status.HTTP_200_OK)

        conversation = [
            {"role": e["role"], "content": e["content"]} for e in echanges
        ]
        interpretation = interpret_duplication_instruction(conversation, source_date, today)

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
