from django.urls import path

from . import views

urlpatterns = [
    path('registrations/', views.RegistrationList.as_view()),
    path('registrations/<int:pk>/', views.RegistrationDetail.as_view()),
]
