import json
import os
from io import BytesIO

import requests
from django.db import models
from django_jsonform.models.fields import JSONField as JSONFormField
from PIL import Image
from utils.abstracts import AbstractClassToLabelModel, AbstractTimestampModel, AbstractUUIDModel

from . import LINE_NAME_MAP, JobStatus, get_activation_alias_schema


class ModelVersion(AbstractUUIDModel, AbstractTimestampModel, AbstractClassToLabelModel):
    is_active = models.BooleanField(default=False)
    model = models.ForeignKey("core.Media", on_delete=models.PROTECT)
    version = models.PositiveSmallIntegerField(default=1, editable=False)
    description = models.TextField(blank=True)
    local_model_path = models.CharField(max_length=255, null=True, blank=True, editable=False)

    class Meta:
        db_table = "model_version"
        verbose_name = "Model Version"
        verbose_name_plural = "Model Versions"
        ordering = ["-created_at"]
        unique_together = (("model", "version"),)

    def __str__(self):
        return f"{self.id}"

    def load_model(self):
        with open("model.pt", "wb") as f:
            res = requests.get(self.model.signed_url)
            f.write(res.content)
        self.local_model_path = os.path.abspath("model.pt")

    def save(self, *args, **kwargs):
        if self.is_active:
            ModelVersion.objects.filter(is_active=True).update(is_active=False)
        if not self.id:
            self.version = ModelVersion.objects.count() + 1
        super().save(*args, **kwargs)


class TestKitGroup(AbstractUUIDModel, AbstractTimestampModel, AbstractClassToLabelModel):
    uid = models.CharField(max_length=255, unique=True)
    activation_alias = JSONFormField(schema=get_activation_alias_schema, blank=True)
    child_sequence = models.PositiveSmallIntegerField(default=0)
    parent_kit = models.ForeignKey(
        "self", on_delete=models.PROTECT, related_name="child_kits", null=True, blank=True
    )

    class Meta:
        db_table = "test_kit_group"
        verbose_name = "Test Kit Group"
        verbose_name_plural = "Test Kit Groups"
        ordering = ["child_sequence", "-created_at"]

    def __str__(self):
        return self.uid

    @property
    def is_combo(self):
        return len(self.child_kits.all()) > 0

    def _get_activation_map(self, activation_alias):
        if not activation_alias:
            return {}
        return {item["activation"]: item["alias"] for item in activation_alias}

    @property
    def activation_map(self):
        child_kits = self.child_kits.all().order_by("child_sequence")
        if child_kits:
            _list = list(map(lambda x: self._get_activation_map(x.activation_alias), child_kits))
            return _list
        return self._get_activation_map(self.activation_alias)


class Job(AbstractUUIDModel, AbstractTimestampModel):
    image = models.ForeignKey("core.Media", on_delete=models.PROTECT)
    status = models.CharField(max_length=127, choices=JobStatus.CHOICES, default=JobStatus.PENDING)
    result = models.JSONField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    model_version = models.ForeignKey(
        "detect.ModelVersion", on_delete=models.PROTECT, related_name="jobs"
    )
    test_kit_group = models.ForeignKey(
        "detect.TestKitGroup", on_delete=models.PROTECT, related_name="jobs", null=True, blank=True
    )

    class Meta:
        db_table = "job"
        verbose_name = "Job"
        verbose_name_plural = "Jobs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.id}"

    def upsert_rtks(self, results):
        for result in results:
            self.results.update_or_create(
                box=result["box"],
                defaults={
                    "name": result["name"],
                    "score": result["confidence"],
                },
            )

    def run(self):
        from ultralytics import YOLO

        data = None
        try:
            model = YOLO(self.model_version.local_model_path, task="detect")
            response = requests.get(self.image.signed_url)
            image = Image.open(BytesIO(response.content))
            results = model.predict(source=image, device="cpu")
            result = results[0] if len(results) else None
            data = json.loads(result.tojson()) if result else []
            self.upsert_rtks(data)
            self.result = data
            self.status = JobStatus.COMPLETED
            self.error = None
        except Exception as e:
            self.error = str(e)
            self.status = JobStatus.FAILED

        self.save()
        return data

    @property
    def class_to_label_map(self):
        if self.test_kit_group and self.test_kit_group.class_to_label:
            return self.test_kit_group.class_to_label_map
        return self.model_version.class_to_label_map

    @property
    def label_to_color_map(self):
        if self.test_kit_group and self.test_kit_group.class_to_label:
            return self.test_kit_group.label_to_color_map
        return self.model_version.label_to_color_map

    @property
    def labels(self):
        if self.test_kit_group and self.test_kit_group.class_to_label:
            return self.test_kit_group.labels
        return self.model_version.labels

    def get_aggregate(self):
        agg_map = {label: 0 for label in self.labels}
        for test_kit in self.results.all():
            agg_map[test_kit.label] += 1
        return agg_map


class TestKit(AbstractUUIDModel, AbstractTimestampModel):
    name = models.CharField(max_length=255)
    score = models.FloatField()
    box = models.JSONField()
    job = models.ForeignKey("detect.Job", on_delete=models.PROTECT, related_name="results")
    is_ok = models.BooleanField(default=True)
    feedback_label = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "test_kit"
        verbose_name = "Test Kit"
        verbose_name_plural = "Test Kits"
        ordering = ["-created_at"]
        unique_together = (("job", "box"),)

    def __str__(self):
        return f"v{self.job.model_version.version} - {self.name}"

    def activations(self, custom_map=None):
        if len(self.name) == 8 and self.name.startswith("C"):
            c0, t1, t2 = map(lambda x: x[1:] == "1", self.name.split("_"))
            activation_map = (
                custom_map
                if isinstance(custom_map, dict)
                else getattr(self.job.test_kit_group, "activation_map", {})
            )
            final_map = {}
            if activation_map.get(LINE_NAME_MAP["C0"]):
                final_map[activation_map.get(LINE_NAME_MAP["C0"])] = c0
            if activation_map.get(LINE_NAME_MAP["T1"]):
                final_map[activation_map.get(LINE_NAME_MAP["T1"])] = t1
            if activation_map.get(LINE_NAME_MAP["T2"]):
                final_map[activation_map.get(LINE_NAME_MAP["T2"])] = t2
            return final_map
        return {}

    @property
    def label(self):
        return self.job.class_to_label_map.get(self.name, "Unknown")

    @property
    def color(self):
        return self.job.label_to_color_map.get(self.label, "")

    def save(self, *args, **kwargs):
        if self.feedback_label:
            self.is_ok = self.feedback_label == self.name
        super().save(*args, **kwargs)
