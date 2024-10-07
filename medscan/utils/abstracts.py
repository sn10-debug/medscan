import uuid

from django.db import models
from django_jsonform.models.fields import JSONField


class AbstractUUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class AbstractTimestampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AbstractEntityModel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        abstract = True


MODEL_CLASSES = [
    "target",
    "C0_T0_T0",
    "C0_T0_T1",
    "C0_T1_T0",
    "C0_T1_T1",
    "C1_T0_T0",
    "C1_T0_T1",
    "C1_T1_T0",
    "C1_T1_T1",
]

OUTPUT_LABELS = [
    "rtk",
    "positive",
    "negative",
    "invalid",
]

CLASS_TO_LABEL_SCHEMA = {
    "type": "array",
    "title": "Config",
    "items": {
        "type": "object",
        "title": "Config Item",
        "keys": {
            "class": {
                "type": "string",
                "choices": MODEL_CLASSES,
            },
            "label": {"type": "string"},
            "color": {"type": "string"},
        },
    },
}


class AbstractClassToLabelModel(models.Model):
    class_to_label = JSONField(schema=CLASS_TO_LABEL_SCHEMA, blank=True)

    class Meta:
        abstract = True

    @property
    def class_to_label_map(self):
        return {item["class"]: item["label"] for item in self.class_to_label}

    @property
    def label_to_color_map(self):
        return {item["label"]: item.get("color", "") for item in self.class_to_label}

    @property
    def labels(self):
        return list(set(self.class_to_label_map.values()))
