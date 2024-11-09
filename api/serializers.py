from build.models import BuildRequest
from flow.models import Flow
from rest_framework import serializers



class BuildRequestSerializer(serializers.HyperlinkedModelSerializer):
    flows = serializers.SerializerMethodField()
    class Meta:
        model = BuildRequest
        fields = ['name', 'url', 'branch', 'flows', 'options']

    def get_flows(self, obj):
        return [flow.name for flow in obj.flows.all()]
