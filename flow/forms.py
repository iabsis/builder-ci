from . import models
from django import forms
from django.forms.models import inlineformset_factory
from django.contrib import messages

FlowFormSet = inlineformset_factory(
    models.Flow, models.Task, fields=('method', 'priority'), extra=1, can_delete=True)


class FlowTestForm(forms.Form):
    data_to_test = forms.CharField(
        widget=forms.Textarea, help_text="Paste the file which is containing version")