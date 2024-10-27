from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import resolve, reverse_lazy, exceptions
from django.template.loader import get_template
from django.template import TemplateDoesNotExist


# Create your views here.

class GenericViewList(LoginRequiredMixin, ListView):

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
        context['create_url'] = self.create_url
        context['delete_url'] = self.delete_url
        context['update_url'] = self.update_url
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


class GenericViewFormUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
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
    

class GenericViewFormCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    template_name = 'form.html'
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


class GenericViewDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    template_name = 'delete.html'
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
    
