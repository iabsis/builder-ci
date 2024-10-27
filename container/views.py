from . import models
from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

# Create your views here.

class ContainerListView(LoginRequiredMixin, ListView):
    model = models.Container

class ContainerCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = models.Container
    fields = ['name', 'dockerfile']
    success_url = reverse_lazy('container')

class ContainerUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = models.Container
    fields = ['name', 'dockerfile']
    success_url = reverse_lazy('container')

class ContainerDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = models.Container
    success_url = reverse_lazy('container')