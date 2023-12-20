from django.contrib import admin

from .models import DiagnosticService, DiagnosticRequest, DiagnosticServiceTracker

admin.site.register(DiagnosticService)
admin.site.register(DiagnosticRequest)
admin.site.register(DiagnosticServiceTracker)