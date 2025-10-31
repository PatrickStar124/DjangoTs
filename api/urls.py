# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('goods/', views.goods_list, name='goods-list'),
    path('goods/<int:id>/', views.good_detail, name='good-detail'),
    path('auth/register/', views.user_register, name='user_register'),
    path('test/', views.test_view, name='test-api'),
    path('auth/login/', views.user_login, name='user_login'),
    path('auth/csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('auth/logout/', views.user_logout, name='user_logout'),
    path('auth/status/', views.check_auth_status, name='check_auth_status'),

    # 🔥 新增：用户商品相关路由
    path('user-goods/<str:action>/', views.user_goods_list, name='user-goods'),
    # 🔥 新增：购买商品路由
    path('goods/<int:id>/purchase/', views.purchase_good, name='purchase-good'),
]