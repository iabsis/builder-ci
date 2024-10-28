from django.core.management.base import BaseCommand
from ... import tasks
from ... import models

class Command(BaseCommand):
    help = 'Build the podman image'

    def add_arguments(self, parser):
        parser.add_argument("action")
        parser.add_argument("--id", nargs='?')

    def handle(self, *args, **options):
        if options.get('action') == 'run':

            tasks.build_run.delay(
                build_id=options.get('id'),
            )
        
        if options.get('action') == 'list':
            for build in models.Build.objects.all():
                print(build)