
from build.models import BuildRequest
from build import tasks
from flow.models import Flow
from rest_framework import permissions, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from . import serializers
# Create your views here.


class BuildRequestViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    queryset = BuildRequest.objects.all()
    serializer_class = serializers.BuildRequestSerializer

    def create(self, request, *args, **kwargs):
        flow_names = request.data.get('flows', [])

        build_request, _ = BuildRequest.objects.update_or_create(
            name=request.data.get('name'),
            url=request.data.get('url'),
            branch=request.data.get('branch'),
            options=request.data.get('options', {}),
        )

        flows = Flow.objects.filter(name__in=flow_names)
        build_request.flows.set(flows)
        build_request.save()

        tasks.build_request.delay(build_request.pk)

        return Response({"detail": f"Build request successfully triggered with ID {build_request.pk}"})


    # def post(self, request, format=None):
    #     content = {
    #         'user': str(request.user),  # `django.contrib.auth.User` instance.
    #         'auth': str(request.auth),  # None
    #     }
    #     return Response(content)



# @method_decorator(csrf_exempt, name='dispatch')
# class BuildView(View):
#     def post(self, request, *args, **kwargs):

#         try:
#             config = json.loads(request.body)
#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Invalid JSON"}, status=400)
        
#         name = config.get('name')
#         url = config.get('url')
#         branch = config.get('branch')
#         flows = config.get('flows')
#         options = config.get('options')

#         build_request, _ = models.BuildRequest.objects.update_or_create(
#             name=name,
#             options=options,
#             url=url,
#             fetch_method=models.SourceFetchMode.GIT,
#             branch=branch,
#         )

#         build_request.flows.clear()

#         if not flows:
#             tasks.build_request.delay(build_request.pk)
#             return JsonResponse({"status": "WARNING", "message": f"No flows provided, trying all..."})

#         for flow_name in flows:
#             try:
#                 flow = Flow.objects.get(name=flow_name)
#             except Flow.DoesNotExist:
#                 return JsonResponse({"status": "ERROR", "message": f"The flow {flow_name} doesn't exist, build not triggered"})
#             build_request.flows.add(flow)

#         tasks.build_request.delay(build_request.pk)
#         return JsonResponse({
#             "status": "SUCCESS",
#             "buildrequest_id": build_request.pk,
#             "detail": f"Buildrequest successfully triggered with ID {build_request.pk}",
#             "url": ""
#             })