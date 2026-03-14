from django.urls import path
from . import views

urlpatterns = [
    path('', views.root_redirect, name='root'),  # ← корень теперь использует root_redirect
    path('<str:username>/email/<str:email_slug>/move/', views.move_email, name='move_email'),
    path('<str:username>/email/<str:email_slug>/', views.email_detail, name='email_detail'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('<str:username>/compose/', views.compose_email, name='compose'),
    path('<str:username>/<str:folder>/', views.email_list, name='email_list'),
    path('<str:username>/', views.inbox, name='inbox'),
]