from django.urls import path

from .views import CreateJob, InferJob, ResultFeedback

urlpatterns = [
    path("job", CreateJob.as_view()),
    path("<slug:job_id>/infer", InferJob.as_view()),
    path("result/feedback", ResultFeedback.as_view()),
]
