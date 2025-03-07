from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('products/', views.products, name='products'),
    path('add-product/', views.add_product, name='add_product'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('upgrade/<int:product_id>/', views.upgrade_listing, name='upgrade_listing'),
    path('payment/success/', views.payment_success, name='payment_success'),  # This line is critical
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('refer/<str:username>/', views.referral_signup, name='referral_signup'),
    path('redeem/<int:product_id>/', views.redeem_credits, name='redeem_credits'),
]