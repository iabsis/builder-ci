from django.core.management.base import BaseCommand
from ... import tasks

class Command(BaseCommand):
    help = 'Build the podman image'

    def add_arguments(self, parser):
        parser.add_argument("action")
        parser.add_argument("container_id")
        parser.add_argument("--image", nargs='?')
        parser.add_argument("--tag", nargs='?')

    def handle(self, *args, **options):
        tasks.build_image(
            container_id=options.get('container_id'),
            image=options.get('image'),
            tag=options.get('tag'),
        )