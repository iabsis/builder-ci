from . import models
from django.forms.models import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Reset

FlowFormSet = inlineformset_factory(
    models.Flow, models.Task, fields=('method', 'priority'), extra=1, can_delete=True)


class FlowFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # print(self.layout)
        # self.layout = Layout(
        #     Row(
        #         Column('priority', css_class='form-group col-md-3 mb-0'),
        #         Column('method', css_class='form-group col-md-3 mb-0'),
        #         css_class='form-row'
        #     ),
        # )