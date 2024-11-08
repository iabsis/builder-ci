import json
from django.shortcuts import render
from django.views import View
from build import tasks, models
from flow.models import Flow
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
        
        name = options.get('name')
        url = options.get('url')
        branch = options.get('branch')
        flows = options.get('flows')

        build_request, _ = models.BuildRequest.objects.update_or_create(
            name=name,
            options=options,
            url=url,
            fetch_method=models.SourceFetchMode.GIT,
            branch=branch,
        )

        for flow in build_request.flows.all():
            flow.delete()

        print(Flow.objects.all())

        for flow_name in flows:
            try:
                flow = Flow.objects.get(name=flow_name)
            except Flow.DoesNotExist:
                return JsonResponse({"status": "ERROR", "message": f"The flow {flow_name} doesn't exist, build not triggered"})
            build_request.flows.add(flow)

        tasks.build_request.delay(build_request.pk)
        return JsonResponse({
            "status": "SUCCESS",
            "buildrequest_id": build_request.pk,
            "message": f"Buildrequest successfully triggered with ID {build_request.pk}",
            "url": ""
            })