import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
from .models import Product, Wallet

class ProductConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.product_id = self.scope['url_route']['kwargs']['product_id']
        self.group_name = f'product_{self.product_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    async def update_views(self, event):
        try:
            views = event['views']
            free_views = event['free_views']
            await self.send(text_data=json.dumps({
                'views': views,
                'free_views': free_views,
            }))
        except KeyError as e:
            print(f"Error in update_views: Missing key {e}")

class AdminDashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('admin_dashboard', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('admin_dashboard', self.channel_name)

    async def receive(self, text_data):
        pass

    async def update_metrics(self, event):
        try:
            await self.send(text_data=json.dumps({
                'total_listings': event['total_listings'],
                'total_purchases': event['total_purchases'],
                'total_users': event['total_users'],
                'total_views': event['total_views'],
            }))
        except KeyError as e:
            print(f"Error in update_metrics: Missing key {e}")

class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'user_{self.user_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    async def update_dashboard(self, event):
        try:
            balance = event['balance']
            await self.send(text_data=json.dumps({
                'balance': balance,
            }))
        except KeyError as e:
            print(f"Error in update_dashboard: Missing key {e}")