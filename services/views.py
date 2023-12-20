from django.db.models import Subquery, OuterRef, Exists
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from labservices.decorators import labstaff_required
from django.shortcuts import render, redirect, get_object_or_404
from userprofile.models import Notification, User
from .forms import DiagnosticServiceForm, DiagnosticRequestForm, DiagnosticTrackerUpdateForm
from .models import DiagnosticService, DiagnosticServiceTracker, DiagnosticRequest


@labstaff_required
def service_list(request):
    services = DiagnosticService.objects.all()

    return render(request, 'services/services_list.html', {
        'services': services
    })


@labstaff_required
def service_detail(request, pk):
    service = get_object_or_404(
        DiagnosticService, created_by=request.user, pk=pk)

    return render(request, 'services/service_detail.html', {
        'service': service
    })


@labstaff_required
def service_delete(request, pk):
    service = get_object_or_404(
        DiagnosticService, created_by=request.user, pk=pk)
    service.delete()
    messages.success(request, "The lab service was deleted")

    return redirect('services:list')


@labstaff_required
def service_edit(request, pk):
    service = get_object_or_404(
        DiagnosticService, created_by=request.user, pk=pk)

    if request.method == 'POST':
        form = DiagnosticServiceForm(request.POST, instance=service)
        if form.is_valid():
            service.save()
            messages.success(request, "The lab service was created")

            return redirect('services:list')

    else:
        form = DiagnosticServiceForm(instance=service)

    return render(request, 'services/service_edit.html', {

        'form': form

    })


@labstaff_required
def add_service(request):
    if request.method == 'POST':
        form = DiagnosticServiceForm(request.POST)

        if form.is_valid():
            service = form.save(commit=False)
            service.created_by = request.user
            service.save()
            messages.success(request, "The service was created")

            return redirect('services:list')
    else:
        form = DiagnosticServiceForm()

    return render(request, 'services/add_services.html', {

        'form': form

    })


@login_required
def request_service_list(request):
    user = request.user
    if user.is_labstaff:
        # Show all requests for lab staff
        requests_services = DiagnosticRequest.objects.all()
    else:
        # For clients, show only their requests
        requests_services = DiagnosticRequest.objects.filter(client=user)

    # Annotate with tracking information
    requests_services = requests_services.annotate(
        latest_status_update=Subquery(
            DiagnosticServiceTracker.objects.filter(
                requested_service=OuterRef('pk')
            ).order_by('-created_at').values('status')[:1]
        ),
        is_tracked=Exists(
            DiagnosticServiceTracker.objects.filter(
                requested_service=OuterRef('pk')
            )
        )
    )

    return render(request, 'services/request_list.html', {'requests_services': requests_services})


@login_required
def request_detail(request, request_id):
    user = request.user
    request_detail_qs = DiagnosticRequest.objects.filter(id=request_id).annotate(
        latest_status_update=Subquery(
            DiagnosticServiceTracker.objects.filter(
                requested_service=OuterRef('pk')
            ).order_by('-created_at').values('status')[:1]
        )
    )
    request_detail = get_object_or_404(request_detail_qs, id=request_id)

    # Allow only the client who made the request or lab staff to view the details
    if not (user.is_labstaff or request_detail.client == user):
        messages.error(
            request, "You do not have permission to access this request.")
        return redirect('services:dashboard')

    # Fetch all updates for the request
    updates = request_detail.service_updates.order_by('-created_at')

    # Handle status update by lab staff
    if user.is_labstaff and request.method == 'POST':
        form = DiagnosticTrackerUpdateForm(request.POST)
        if form.is_valid():
            update = form.save(commit=False)
            update.requested_service = request_detail
            update.updated_by = user
            update.save()

            Notification.objects.create(
                recipient=request_detail.client,
                message=f"Status of your request '{request_detail.service.get_name_display()}' has been updated."
            )
            messages.success(request, "Status updated successfully.")
            return redirect('services:request_list')
    else:
        form = DiagnosticTrackerUpdateForm() if user.is_labstaff else None

    return render(request, 'services/request_detail.html', {
        'request_detail': request_detail,
        'latest_status_update': request_detail.latest_status_update,
        'updates': updates,
        'form': form,  # Include form in context only for lab staff
    })


@login_required
def request_service(request):
    if not request.user.is_client:
        return redirect('client:403')

    if request.method == 'POST':
        form = DiagnosticRequestForm(request.POST)
        if form.is_valid():
            diagnostic_request = form.save(commit=False)
            diagnostic_request.client = request.user
            diagnostic_request.save()

            # Notify staff members about the new request
            staff_members = User.objects.filter(is_labstaff=True)
            for staff_member in staff_members:
                Notification.objects.create(
                    recipient=staff_member,
                    message=f"A new request has been made by {request.user.username}."
                )

            return redirect('services:request_list')
    else:
        form = DiagnosticRequestForm()

    return render(request, 'services/request_service.html', {'form': form})
