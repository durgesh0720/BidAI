# marketplace/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/admin_dashboard/$', consumers.AdminDashboardConsumer.as_asgi()),
    re_path(r'ws/product/(?P<product_id>\d+)/$', consumers.ProductConsumer.as_asgi()),
    re_path(r'ws/dashboard/(?P<user_id>\d+)/$', consumers.DashboardConsumer.as_asgi()),
]