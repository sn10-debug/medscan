from detect.models import ModelVersion
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load the latest active model in memory"

    def add_arguments(self, parser):
        """Optional argument which takes in model version"""
        parser.add_argument("model_version", nargs="?", type=int)

    def handle(self, *args, **options):
        """Load the latest active model in memory"""
        model_version = ModelVersion.objects.filter(is_active=True).order_by("-updated_at").first()
        if options.get("model_version", None) is not None:
            model_version = (
                ModelVersion.objects.filter(version=options["model_version"])
                .order_by("-updated_at")
                .first()
            )
        if model_version is None:
            self.stdout.write(self.style.ERROR("no active model version found"))
            return
        model_version.load_model()
        model_version.save()

        self.stdout.write(
            self.style.SUCCESS('successfully loaded model version "%d"' % model_version.version)
        )
