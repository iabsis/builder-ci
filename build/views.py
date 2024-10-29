from django.views import View
from django.http import JsonResponse
from . import models, tasks

# Create your views here.

class Build(View):
    def post(self, request, *args, **kwargs):

        build_request = models.BuildRequest.objects.create(
            name=kwargs.get('name')
        )

        tasks.build_trigger.delay(build_request.pk)
        JsonResponse({"test": "test"})