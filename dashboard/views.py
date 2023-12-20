from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from userprofile.models import LabStaff, Client, Notification

@login_required
def dashboard(request):
    user = request.user
    context = {}

    if user.is_labstaff:
        context['user_type'] = 'labstaff'
        context['labstaff_info'] = get_object_or_404(LabStaff, user=user)
    elif user.is_client:
        context['user_type'] = 'client'
        context['client_info'] = get_object_or_404(Client, user=user)
    else:
        context['user_type'] = 'other'

    return render(request, 'dashboard/dashboard.html', context)



