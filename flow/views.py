from . import models, forms
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from sbadmin2.views import GenericViewFormCreate, GenericViewFormUpdate
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

class FlowCreateView(GenericViewFormCreate):
    model = models.Flow

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['child_formset'] = forms.FlowFormSet(
            instance=self.object, prefix='child_formset')
        return context

    def form_valid(self, form):
        self.object = form.save()
        child_formset = forms.FlowFormSet(
            self.request.POST, instance=self.object, prefix='child_formset')
        if child_formset.is_valid():
            child_formset.save()
            success_message = self.get_success_message(form.cleaned_data)
            if success_message:
                messages.success(self.request, success_message)
        else:
            messages.warning(
                self.request, 'Unable to save some aliases, some symbols are probably duplicated.')
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class FlowUpdateView(GenericViewFormUpdate):
    model = models.Flow

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['child_formset'] = forms.FlowFormSet(
            instance=self.object, prefix='child_formset')
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        child_formset = forms.FlowFormSet(
            self.request.POST, instance=self.object, prefix='child_formset')
        if child_formset.is_valid():
            child_formset.save()
            success_message = self.get_success_message(form.cleaned_data)
            if success_message:
                messages.success(self.request, success_message)
        else:
            messages.warning(
                self.request, 'Unable to save some aliases, some symbols are probably duplicated.')
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class FlowTestView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    success_url = reverse_lazy('flow')
    form_class = forms.FlowTestForm
    template_name = 'form.html'

    def post(self, request, *args, **kwargs):
        flow = get_object_or_404(
            models.Flow, pk=kwargs['pk'])
        form = self.form_class(request.POST)
        if form.is_valid():
            data_to_test = form.cleaned_data['data_to_test']
            try:
                version = flow.get_version_content(data_to_test)
            except Exception as e:
                form.add_error(None, f"This data didn't returned version: {e}")
                return render(request, self.template_name, {'form': form})
            messages.success(
                request, f"Success! The version has been founded: {version}")
            return HttpResponseRedirect(self.get_success_url())
