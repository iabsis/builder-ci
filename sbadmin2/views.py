from django.views.generic import ListView, UpdateView, CreateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import resolve, reverse_lazy, reverse
from django.template.loader import get_template
from django.urls import get_resolver
from django.template import TemplateDoesNotExist
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator

# Create your views here.

def named_url_exist(name):
    for x in get_resolver(None).reverse_dict.items():
        if x[0] == name:
            return True
    return False

class GenericViewList(LoginRequiredMixin, ListView):
    paginate_by = 10

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
        return context
   
    def get_queryset(self):
        queryset = super().get_queryset()

        query_filter = {}
        for key, value in self.request.GET.items():
          if key.startswith('filter_'):
            query_filter[key.replace('filter_', '')] = value
        queryset = queryset.filter(**query_filter)
        return queryset

    def get_template_names(self):
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        default_template_name = f"{app_label}/{model_name}_list.html"

        try:
            get_template(default_template_name)
            return [default_template_name]
        except TemplateDoesNotExist:
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
            return ['detail.html']

class UserLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

class UserLogoutView(LogoutView):
    template_name = 'logout.html'