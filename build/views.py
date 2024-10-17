from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from . import models
from . import tasks
import json
# Create your views here.


@method_decorator(csrf_exempt, name='dispatch')
class Build(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        obj = models.Build.objects.create(
            name=data['project'],
            options={
                "sources": data.get('sources'),
                "notify": data.get('notify'),
                "builder": data.get('builder'),
                "publish": data.get('publish'),
                "patcher": data.get('patcher')
            }
        )

        tasks.run_build.delay(obj.pk)

        return JsonResponse({
            "result": "success",
            "id": obj.pk})
