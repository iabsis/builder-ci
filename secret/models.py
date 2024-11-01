from django.db import models
import pgcrypto

# Create your models here.


class Secret(models.Model):
    name = models.CharField(max_length=50)
    secret = pgcrypto.EncryptedTextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
