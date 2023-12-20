from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from userprofile.models import User, Client, LabStaff
from services.models import DiagnosticService


class LabStaffSignUpForm(UserCreationForm):
    position = forms.CharField(required=True)
    #start_date = forms.DateField(required=True)
    profession = forms.CharField(required=True)
    degrees = forms.CharField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_labstaff = True
        user.save()
        LabStaff.objects.create(
            user=user,
            position=self.cleaned_data.get('position'),
            #start_date=self.cleaned_data.get('start_date'),
            profession=self.cleaned_data.get('profession'),
            degrees=self.cleaned_data.get('degrees')
        )
        return user


class ClientSignUpForm(UserCreationForm):
    selected_diagnostics = forms.ModelMultipleChoiceField(
        queryset=DiagnosticService.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_client = True
        user.save()
        client = Client.objects.create(user=user)
        client.selected_diagnostics.add(*self.cleaned_data.get('selected_diagnostics'))
        return user
