from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings





class User(AbstractUser):

    
    is_labstaff = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)


class LabStaff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    position = models.CharField(max_length=100, verbose_name="Position in Lab")
    #start_date = models.DateField(verbose_name="Start Date")
    profession = models.CharField(max_length=100, verbose_name="Profession")
    degrees = models.CharField(max_length=200, verbose_name="Degrees/Certifications")

    class Meta:
        ordering = ['user__username']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.position})"


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    description = models.TextField(blank=True, null=True)
    selected_diagnostics = models.ManyToManyField('services.DiagnosticService', related_name='clients', blank=True)

    class Meta:
        ordering = ['user__username']

    def __str__(self):
        return f"{self.user.get_full_name()}"


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.username} - Read: {self.read}"
