import json
from django.shortcuts import render
from django.views import View
from build import tasks, models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Create your views here.


@method_decorator(csrf_exempt, name='dispatch')
class BuildView(View):
    def post(self, request, *args, **kwargs):

        try:
            options = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        
        name = options['project']

        url = options['sources']['options']['url']
        branch = options['sources']['options']['branch']
        del options['project']

        build_request = models.BuildRequest.objects.create(
            name=name,
            options=options,
            url=url,
            fetch_method=models.SourceFetchMode.GIT,
            branch=branch,
        )

        tasks.build_request.delay(build_request.pk)
        return JsonResponse({"status": "SUCCESS", "buildrequest_id": build_request.pk})