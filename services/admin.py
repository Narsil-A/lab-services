from django.contrib import admin

from .models import DiagnosticService, DiagnosticRequest, DiagnosticServiceTracker, Payment

admin.site.register(DiagnosticService)
admin.site.register(DiagnosticRequest)
admin.site.register(DiagnosticServiceTracker)
admin.site.register(Payment)