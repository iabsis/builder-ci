from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# Create your models here.

class MatrixInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    room_id = models.CharField(max_length=255, null=True, blank=True)

class UserMatrixProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='matrix_profile')
    matrix_account = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^@[a-zA-Z0-9._=-]+:[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                message='Matrix account must be in format @username:domain (e.g., @user:matrix.org)',
                code='invalid_matrix_id'
            )
        ],
        help_text='Your Matrix ID in format @username:domain (e.g., @user:matrix.org)'
    )
    matrix_notifications_enabled = models.BooleanField(
        default=False,
        help_text='Enable Matrix notifications for build status updates'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Matrix Profile"

    class Meta:
        verbose_name = "User Matrix Profile"
        verbose_name_plural = "User Matrix Profiles"
