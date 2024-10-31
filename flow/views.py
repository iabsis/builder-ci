from . import models, forms
from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from sbadmin2.views import GenericViewList, GenericViewFormCreate, GenericViewFormUpdate
from django.contrib import messages
from django.http import HttpResponseRedirect

class FlowCreateView(GenericViewFormCreate):
    model = models.Flow

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['child_formset'] = forms.FlowFormSet(
            instance=self.object, prefix='child_formset')
        return context

    def form_valid(self, form):
        print("BLA")
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


class FlowUpdateView(GenericViewFormUpdate):
    model = models.Flow

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['child_formset'] = forms.FlowFormSet(
            instance=self.object, prefix='child_formset')
        # context['child_formset_helper'] = forms.FlowFormSetHelper()
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        child_formset = forms.FlowFormSet(
            self.request.POST, instance=self.object, prefix='child_formset')
        print(child_formset.non_form_errors())
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
