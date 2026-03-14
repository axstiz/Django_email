from django.urls import path
from . import views

urlpatterns = [
    path('', views.root_redirect, name='root'),
    path('register/', views.register_view, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('<str:username>/', views.inbox, name='inbox'),
    path('<str:username>/compose/', views.compose_email, name='compose'),
    path('<str:username>/drafts/<str:email_slug>/edit/', views.edit_draft, name='edit_draft'),
    path('<str:username>/<str:folder>/', views.email_list, name='email_list'),
    path('<str:username>/email/<str:email_slug>/', views.email_detail, name='email_detail'),
    path('<str:username>/email/<str:email_slug>/move/', views.move_email, name='move_email'),
    path('<str:username>/email/<str:email_slug>/delete/', views.delete_email, name='delete_email'),
]
