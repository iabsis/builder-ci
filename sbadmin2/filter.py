import django_filters
from django.db.models import JSONField, Field

def get_filterset_for_model(model):
    class AutoFilterSet(django_filters.FilterSet):
        def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
            super().__init__(data, queryset, request=request, prefix=prefix)
        class Meta:
            model = model
            exclude = [
                f.name for f in model._meta.get_fields()
                if isinstance(f, JSONField)
            ]
    return AutoFilterSet