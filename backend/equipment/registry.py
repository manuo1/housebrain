"""
Registry of concrete Equipment models exposed via the API — one entry per
type. Mirrors the pattern of device.catalog.DEVICE_MODELS: adding a new
equipment type (e.g. a future RollerShutter) means adding it here, no
other generic code (selectors/views) needs to change.
"""

from equipment.models import GarageDoor

EQUIPMENT_MODELS = [GarageDoor]

EQUIPMENT_MODELS_BY_NAME = {model._meta.model_name: model for model in EQUIPMENT_MODELS}
