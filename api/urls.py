from django.urls import path
from . import views

urlpatterns = [
    path('goods/', views.goods_list, name='goods-list'),
    path('goods/<int:id>/', views.good_detail, name='good-detail'),
    path('auth/register/', views.user_register, name='user_register'),
    path('test/', views.test_view, name='test-api'),
    path('auth/login/', views.user_login, name='user_login'),
    path('auth/csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('auth/logout/', views.user_logout, name='user_logout'),
    path('auth/status/', views.check_auth_status, name='check_auth_status'),
]