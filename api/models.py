from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MANAGER = 'manager', 'Manager'
        USER = 'user', 'User'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER
    )

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def is_manager(self):
        return self.role == self.Role.MANAGER

class Resource(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
