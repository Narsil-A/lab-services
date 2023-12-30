import stripe
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Subquery, OuterRef, Exists, Sum
from django.contrib import messages

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from labservices.decorators import labstaff_required
from django.shortcuts import render, redirect, get_object_or_404

from userprofile.models import Notification, User
from .forms import DiagnosticServiceForm, DiagnosticRequestForm, DiagnosticTrackerUpdateForm
from .models import DiagnosticService, DiagnosticServiceTracker, DiagnosticRequest, Payment


stripe.api_key = settings.STRIPE_SECRET_KEY


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

    services = DiagnosticService.objects.all()

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

    context = {
        'form': form,
        'services': services
    }
    return render(request, 'services/request_service.html', context)







@login_required
def make_payment(request):
    if not request.user.is_client:
        messages.error(request, "Only clients can make payments.")
        return redirect('services:dashboard')

    diagnostic_requests = DiagnosticRequest.objects.filter(client=request.user, payments__isnull=True)
    if not diagnostic_requests.exists():
        messages.info(request, "You have no unpaid diagnostic requests.")
        return redirect('services:dashboard')

    total_cost = diagnostic_requests.aggregate(Sum('service__cost'))['service__cost__sum']

    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Initialize Stripe API
            stripe.api_key = settings.STRIPE_SECRET_KEY

            # Create a Stripe Payment Intent
            intent = stripe.PaymentIntent.create(
                amount=int(total_cost * 100),  # Convert to cents
                currency='usd',
                payment_method_types=['card']
            )

            # Return the client secret in a JSON response
            return JsonResponse({'client_secret': intent.client_secret})

        # Create a Payment record
        payment = Payment.objects.create(
            user=request.user,
            stripe_payment_intent_id=intent.id,
            paid_amount=total_cost,
            currency='USD'
        )

        # Link payment with all diagnostic requests
        payment.diagnostic_requests.set(diagnostic_requests)

    # Handling GET request
    return render(request, 'services/payment.html', {
        'diagnostic_requests': diagnostic_requests,
        'total_cost': total_cost
    })


@login_required
@csrf_exempt  
def payment_success(request):
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')

        # Retrieve the payment object
        payment = get_object_or_404(Payment, stripe_payment_intent_id=payment_id)

        # Check if the payment is associated with the current user
        if payment.user != request.user:
            return JsonResponse({'message': 'Unauthorized'}, status=401)

        # Update the payment status to 'Completed'
        payment.status = Payment.COMPLETED
        payment.save()

        # Retrieve and update all diagnostic requests linked to this payment
        diagnostic_requests = payment.diagnostic_requests.all()
        for request in diagnostic_requests:
            # Update each request as needed, e.g., change a status field
            # request.status = 'Paid'  # Example status update, adjust according to your model
            request.save()

        return JsonResponse({'message': 'Payment processed successfully'})

    return JsonResponse({'message': 'Invalid request'}, status=400)

@login_required
def payment_succeed(request):
    return render(request, 'pay_success.html')