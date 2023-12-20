
from django import forms

from .models import DiagnosticService, DiagnosticServiceTracker, DiagnosticRequest


class DiagnosticServiceForm(forms.ModelForm):
    class Meta:
        model = DiagnosticService
        fields = '__all__'

class DiagnosticRequestForm(forms.ModelForm):
    class Meta:
        model = DiagnosticRequest
        fields = ['service'] 

class DiagnosticServiceTrackerForm(forms.ModelForm):
    class Meta:
        model = DiagnosticServiceTracker
        fields = '__all__'

class DiagnosticTrackerUpdateForm(forms.ModelForm):
    class Meta:
        model = DiagnosticServiceTracker
        fields = ['status', 'notes']