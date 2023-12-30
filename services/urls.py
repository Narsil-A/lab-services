from django.urls import path


from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='list'),
    path('<int:pk>/', views.service_detail, name='detail'),
    path('<int:pk>/delete/', views.service_delete, name='delete'),
    path('<int:pk>/edit/', views.service_edit, name='edit'),
    path('add-service/', views.add_service, name='add_service'),
    path('request-service/', views.request_service, name='request_service'),
    path('payment/', views.make_payment, name='make_payment'),
    path('payment/success/', views.payment_success, name='payment_success'), 
    path('payment/success_page/', views.payment_succeed, name='payment_succeed'),  
    path('request-service-list/', views.request_service_list, name='request_list'),
    path('<int:request_id>/request-detail/', views.request_detail, name='detail_service'),
]