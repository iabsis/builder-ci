from django.test import TestCase
from . import models

# Create your tests here.


class Container(TestCase):

    def setUp(self):

        container = models.Container.objects.create(
            name="deb-package",
            dockerfile="FROM {{distrib}}:{{codename}}",
            target_tag="builder-{{distrib}}-{{codename}}",
            default_options={"distrib": "debian", "codename": "bookworm"}
        )

        builtcontainer1 = models.BuiltContainer.objects.get_or_create(
            options={'distrib': 'debian', 'codename': 'buster', 'name': 'test'},
            container=container,
        )

        builtcontainer2 = models.BuiltContainer.objects.get_or_create(
            options={'distrib': 'debian', 'codename': 'bookworm', 'name': 'test'},
            container=container,
        )


    def test_target_tag(self):
        container = models.Container.objects.get(name="deb-package")
        builtcontainer = models.BuiltContainer.objects.get(name='builder-debian-buster')
        assert builtcontainer.name == 'builder-debian-buster'