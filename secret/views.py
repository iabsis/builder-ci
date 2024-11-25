from django.shortcuts import render
from . import models
from sbadmin2.views import GenericViewFormUpdate
# Create your views here.

class SecretUpdateView(GenericViewFormUpdate):
    model = models.Secret
    permission_required = "secret.update_secret"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        stars = '*' * ( len(form.initial['secret']) - 1 )
        form.initial['secret'] = form.initial['secret'][:3] + stars
        return form