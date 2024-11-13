
from build.models import BuildRequest, BuildRequestMode
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
            refname=request.data.get('refname'),
            requested_by=request.data.get('requested_by'),
            options=request.data.get('options', {}),
        )

        build_request.modes=request.data.get('modes', "ON_VERSION"),
        flows = Flow.objects.filter(name__in=flow_names)
        build_request.flows.set(flows)
        build_request.save()

        tasks.build_request.delay(build_request.pk)

        return Response({"detail": f"Build request successfully triggered with ID {build_request.pk}"})
