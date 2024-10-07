from detect.models import Job, ModelVersion, TestKit, TestKitGroup
from detect.tasks import infer_single_job
from django.http import JsonResponse
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from utils.exceptions import MissingImageException, MissingKitIDException, MissingModelException
from utils.helpers import save_image

from .serializers import JobSerializer, TestKitSerializer


class CreateJob(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        image = request.FILES.get("image", None)
        kit_group_id = request.data.get("kit_id", None)
        if not image:
            raise MissingImageException()
        if not kit_group_id:
            raise MissingKitIDException()
        current_model = ModelVersion.objects.filter(is_active=True).first()
        test_kit_group = (
            TestKitGroup.objects.get_or_create(
                uid=kit_group_id, defaults={"class_to_label": list(), "activation_alias": list()}
            )[0]
            if kit_group_id
            else None
        )
        if not current_model:
            raise MissingModelException()

        media = save_image(image=image, path="images/")
        job = current_model.jobs.create(image=media, test_kit_group=test_kit_group)
        infer_single_job.apply_async(args=[job.id])
        serializer = JobSerializer(job)
        return JsonResponse(
            {
                "status": "success",
                "code": "job_created",
                "message": "Job created successfully.",
                "data": serializer.data,
            }
        )


class InferJob(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id, *args, **kwargs):
        job = Job.objects.get(id=job_id)
        serializer = JobSerializer(job)
        return JsonResponse(
            {
                "status": "success",
                "code": "job_fetched",
                "message": "Job fetched successfully.",
                "data": serializer.data,
            }
        )


class FeedbackInputSerializer(serializers.Serializer):
    result_id = serializers.CharField(required=True)
    feedback_label = serializers.CharField(required=True)


class ResultFeedback(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        fserializer = FeedbackInputSerializer(data=request.data)
        fserializer.is_valid(raise_exception=True)
        data = fserializer.validated_data
        test_kit = TestKit.objects.get(id=data["result_id"])
        test_kit.is_ok = data["feedback_label"] == test_kit.label
        test_kit.feedback_label = data["feedback_label"]
        test_kit.save()
        rserializer = TestKitSerializer(test_kit)
        return JsonResponse(
            {
                "status": "success",
                "code": "feedback_updated",
                "message": "Feedback updated successfully.",
                "data": rserializer.data,
            }
        )
