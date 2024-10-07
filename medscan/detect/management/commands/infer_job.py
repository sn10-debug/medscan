from detect.tasks import infer_multiple_jobs, infer_single_job
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Infer the provided job id or all pending jobs."

    def add_arguments(self, parser):
        """Optional argument which takes in respective job_id"""
        parser.add_argument("job_id", nargs="?", type=str)

    def handle(self, *args, **options):
        """Infer the provided job id"""
        result = None
        job_id = options.get("job_id", None)
        if job_id is None:
            result = infer_multiple_jobs()
        else:
            result = infer_single_job(job_id)
        self.stdout.write(
            self.style.SUCCESS('successfully infered job "%s" with result "%s"' % (job_id, result))
        )
