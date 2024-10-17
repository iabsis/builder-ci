from django.core.management.base import BaseCommand, CommandError
from ... import tasks

class Command(BaseCommand):
    help = 'Build management'

    def add_arguments(self, parser):
        parser.add_argument("action")
        parser.add_argument("--id", type=int, nargs='?')

    def handle(self, *args, **options):
        if options.get('action') == 'run':
            if not options.get('id') or not isinstance(options.get('id'), int):
                print("ID is mandatory for running build and must be an integer")
                exit(1)
            
            tasks.run_build(options.get('id'))