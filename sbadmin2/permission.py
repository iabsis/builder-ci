from django.contrib.auth.mixins import PermissionRequiredMixin

class DynamicPermissionMixin(PermissionRequiredMixin):
    def get_permission_required(self):
        """
        Dynamically determine the permission based on the model name.
        Additionally, check the type of view using self.__class__.
        """
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        view_type = self.__class__.__name__  # Get the name of the current view class
        print(f"Current view type: {view_type}")  # Debug or log this information

        if view_type == 'GenericViewDelete':
            return [f"{app_label}.delete_{model_name}"]
        elif view_type == 'GenericViewList':
            return [f"{app_label}.view_{model_name}"]
        elif view_type == 'GenericViewDetail':
            return [f"{app_label}.view_{model_name}"]
        elif view_type == 'GenericViewFormCreate':
            return [f"{app_label}.add_{model_name}"]
        elif view_type == 'GenericViewFormUpdate':
            return [f"{app_label}.change_{model_name}"]
        
        # Default permission if no specific case matches
        return [f"{app_label}.view_{model_name}"]
