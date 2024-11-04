from django.views.generic import ListView, UpdateView, CreateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import resolve, reverse_lazy
from django.template.loader import get_template
from django.urls import get_resolver
from django.template import TemplateDoesNotExist
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django_filters.views import FilterView, filterset_factory
from django.db import models
import logging
# Create your views here.

logger = logging.getLogger(__name__)

def named_url_exist(name):
    for x in get_resolver(None).reverse_dict.items():
        if x[0] == name:
            return True
    return False

# class GenericFilterViewList(LoginRequiredMixin, FilterView):


class GenericViewList(LoginRequiredMixin, FilterView):
    paginate_by = 10
    # filterset_fields = ['__all__']

    @property
    def view_url(self):
        return resolve(
            self.request.path_info).url_name + '_view'

    @property
    def create_url(self):
        return resolve(
          self.request.path_info).url_name + '_create'

    @property
    def delete_url(self):
        return resolve(
          self.request.path_info).url_name + '_delete'

    @property
    def update_url(self):
        return resolve(
          self.request.path_info).url_name + '_update'

    def get_filterset_class(self):
        filtered_fields = []
        for field in self.model._meta.fields:
            if isinstance(field, models.CharField):
                filtered_fields.append(field.name)
            if isinstance(field, models.ForeignKey):
                filtered_fields.append(field.name)
        return filterset_factory(model=self.model, fields=filtered_fields)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.model.__name__
        context['field_list'] = [
            field.name for field in self.model._meta.fields]
        if named_url_exist(self.create_url):
            context['create_url'] = self.create_url
        if named_url_exist(self.delete_url):
            context['delete_url'] = self.delete_url
        if named_url_exist(self.update_url):
            context['update_url'] = self.update_url
        if named_url_exist(self.view_url):
            context['view_url'] = self.view_url

        filter_args = self.filterset.data.copy()
        if filter_args.get('page'):
            del filter_args['page']
        context['filter_args'] = "&" + "&".join([f"{key}={value}" for key, value in filter_args.items()])

        return context
   
    # def get_queryset(self):
    #     queryset = super().get_queryset()

        # query_filter = {}
        # for key, value in self.request.GET.items():
        #   if key.startswith('filter_'):
        #     query_filter[key.replace('filter_', '')] = value
        # queryset = queryset.filter(**query_filter)
        # print(self.filterset_class)
        # return queryset

    def get_template_names(self):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        default_template_name = f"{app_label}/{model_name}_list.html"

        try:
            get_template(default_template_name)
            return [default_template_name]
        except TemplateDoesNotExist:
            if settings.DEBUG:
                logger.info(f"{default_template_name} not found, falling to default")
            return ['list.html']


class GenericViewFormUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'form.html'
    success_message = "Update successful"
    fields = "__all__"

    @property
    def list_url(self):
        return resolve(
          self.request.path_info).url_name.replace('_update', '')

    def get_success_url(self):
            return reverse_lazy(self.list_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.model.__name__
        context['list_url'] = self.list_url
        return context

    def get_template_names(self):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        default_template_name = f"{app_label}/{model_name}_update.html"

        try:
            get_template(default_template_name)
            return [default_template_name]
        except TemplateDoesNotExist:
            if settings.DEBUG:
                logger.info(f"{default_template_name} not found, falling to default")
            return ['form.html']


class GenericViewFormCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    success_message = "Create successful"
    fields = "__all__"

    @property
    def list_url(self):
        return resolve(
          self.request.path_info).url_name.replace('_create', '')

    def get_success_url(self):
            return reverse_lazy(self.list_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.model.__name__
        context['list_url'] = self.list_url
        return context

    def get_template_names(self):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        default_template_name = f"{app_label}/{model_name}_create.html"

        try:
            get_template(default_template_name)
            return [default_template_name]
        except TemplateDoesNotExist:
            if settings.DEBUG:
                logger.info(f"{default_template_name} not found, falling to default")
            return ['form.html']

class GenericViewDelete(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    success_message = "Deletion successful"

    @property
    def list_url(self):
        return resolve(
          self.request.path_info).url_name.replace('_delete', '')

    def get_success_url(self):
            return reverse_lazy(self.list_url)

    def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context['list_url'] = self.list_url
      return context

    def get_template_names(self):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        default_template_name = f"{app_label}/{model_name}_delete.html"

        try:
            get_template(default_template_name)
            return [default_template_name]
        except TemplateDoesNotExist:
            if settings.DEBUG:
                logger.info(f"{default_template_name} not found, falling to default")
            return ['delete.html']

class GenericViewDetail(LoginRequiredMixin, DetailView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_list'] = [
            field.name for field in self.model._meta.fields]
        return context

    def get_template_names(self):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        default_template_name = f"{app_label}/{model_name}_detail.html"

        try:
            get_template(default_template_name)
            return [default_template_name]
        except TemplateDoesNotExist:
            if settings.DEBUG:
                logger.info(f"{default_template_name} not found, falling to default")
            return ['detail.html']

class UserLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

class UserLogoutView(LogoutView):
    template_name = 'logout.html'