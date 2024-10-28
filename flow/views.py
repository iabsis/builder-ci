from . import models
from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

# Create your views here.
