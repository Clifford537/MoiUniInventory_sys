from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('add/', views.add_product_view, name='add_product'),
    path('transaction/', views.transaction_view, name='transaction'),
    path('add_store/', views.add_store_view, name='add_store'),
    path('manage_items/', views.manage_items_view, name='manage_items'),
    path('manage_stores/', views.manage_stores_view, name='manage_stores'),
    path('edit_product/<int:product_id>/', views.edit_product_view, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product_view, name='delete_product'),
    path('edit_store/<int:store_id>/', views.edit_store_view, name='edit_store'),
    path('delete_store/<int:store_id>/', views.delete_store_view, name='delete_store'),
]
