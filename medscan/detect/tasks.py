from detect.models import Job, JobStatus

from medscan.celery import app


@app.task(name="main.infer_single_job")
def infer_single_job(job_id):
    job = Job.objects.get(id=job_id)
    if job.status in [JobStatus.PENDING, JobStatus.FAILED]:
        job.run()
    return (job_id, job.status)


@app.task(name="main.infer_multiple_jobs")
def infer_multiple_jobs(
    job_ids=[], job_filter={"status__in": [JobStatus.PENDING, JobStatus.FAILED]}
):
    results = []
    jobs = Job.objects.filter(**job_filter)
    if len(job_ids) > 0:
        jobs = jobs.filter(id__in=job_ids)
    for job in jobs:
        result = infer_single_job(str(job.id))
        results.append(result)
    return results
