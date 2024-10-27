from . import models
from django.shortcuts import render
from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

class ContainerListView(LoginRequiredMixin, ListView):
    model = models.Container

class ContainerUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Container
    fields = '__all__'

