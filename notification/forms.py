from django import forms
from django.contrib.auth.models import User
from .models import UserMatrixProfile


class UserMatrixProfileForm(forms.ModelForm):
    class Meta:
        model = UserMatrixProfile
        fields = ['matrix_account', 'matrix_notifications_enabled']
        widgets = {
            'matrix_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '@username:matrix.org',
                'help_text': 'Enter your Matrix ID in format @username:domain'
            }),
            'matrix_notifications_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['matrix_account'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '@username:matrix.org'
        })
        self.fields['matrix_notifications_enabled'].widget.attrs.update({
            'class': 'form-check-input'
        })