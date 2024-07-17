from django.urls import path
from .views import register_view, login_view,logout_view,check_login_status

urlpatterns = [
    path('register/', register_view, name='register'),
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('check_login_status/', check_login_status, name='check_login_status'),
]
