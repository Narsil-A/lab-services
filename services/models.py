from django.db import models
from userprofile.models import User


class DiagnosticService(models.Model):
    BRUCELLOSIS = 'BRU'
    MYCOBACTERIA_BOVINA = 'MYC'
    LEPTOSPIROSIS = 'LEP'
    RABIA = 'RAB'
    FIEBRE_AFTOSA = 'FIE'

    DIAGNOSTIC_CHOICES = [
        (BRUCELLOSIS, 'Brucellosis'),
        (MYCOBACTERIA_BOVINA, 'Mycobacteria Bovina'),
        (LEPTOSPIROSIS, 'Leptospirosis'),
        (RABIA, 'Rabia'),
        (FIEBRE_AFTOSA, 'Fiebre Aftosa'),
    ]
    name = models.CharField(max_length=3, choices=DIAGNOSTIC_CHOICES)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cost in dollars")
    duration = models.IntegerField(help_text="Duration in days")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='created_diagnostic_services', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.get_name_display()
    

class DiagnosticRequest(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(DiagnosticService, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service.get_name_display()} for {self.client.username}"
    

    
class DiagnosticServiceTracker(models.Model):
    SAMPLE_RECEIVED = 'RECEIVED'
    PROCESSING = 'PROCESSING'
    RESULTS_READY = 'RESULTS_READY'
    STATUS_CHOICES = [
        (SAMPLE_RECEIVED, 'Sample Received'),
        (PROCESSING, 'Processing Samples'),
        (RESULTS_READY, 'Results Ready'),
    ]
    requested_service = models.ForeignKey(DiagnosticRequest, on_delete=models.CASCADE, null=True, related_name='service_updates')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    is_tracked = models.BooleanField(default=False)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_updates')
    notes = models.TextField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='tracke_diagnostic_services', on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.requested_service.service} - {self.get_status_display()}"