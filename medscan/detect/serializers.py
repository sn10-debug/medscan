from itertools import zip_longest

from django.db.models import F, FloatField, Window
from django.db.models.expressions import ExpressionWrapper
from django.db.models.functions import Cast, Lag
from rest_framework import serializers

from .models import Job, TestKit


class TestKitSerializer(serializers.ModelSerializer):
    activations = serializers.SerializerMethodField()

    class Meta:
        model = TestKit
        fields = [
            "id",
            "name",
            "score",
            "label",
            "color",
            "feedback_label",
            "is_ok",
            "box",
            "activations",
        ]

    def get_activations(self, obj):
        custom_map = self.context.get("activation_map", None)
        return obj.activations(custom_map)


class JobSerializer(serializers.ModelSerializer):
    results = serializers.SerializerMethodField()
    signed_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            "id",
            "signed_image_url",
            "status",
            "results",
        ]

    def parse_combo_results(self, obj):
        results = []
        queryset = (
            obj.results.exclude(name="target")
            .annotate(
                curr_x=Cast(F("box__x1"), FloatField()),
                prev_x=Window(expression=Lag("curr_x"), order_by=F("curr_x").asc()),
                diff_x=ExpressionWrapper(F("curr_x") - F("prev_x"), output_field=FloatField()),
            )
            .order_by(F("diff_x").desc(nulls_first=True), F("score").desc())
        )
        activation_list = getattr(obj.test_kit_group, "activation_map", [])
        for result, activation_map in zip_longest(queryset, activation_list, fillvalue={}):
            if result:
                serializer = TestKitSerializer(result, context={"activation_map": activation_map})
                results.append(serializer.data)
        return results

    def get_results(self, obj):
        if getattr(obj.test_kit_group, "is_combo", False):
            return self.parse_combo_results(obj)
        queryset = obj.results.exclude(name="target").order_by("-score")
        serializer = TestKitSerializer(queryset, many=True)
        return serializer.data

    def get_signed_image_url(self, obj):
        # 1 day expiration time
        return obj.image.signed_url_with_expiration(86_400)
