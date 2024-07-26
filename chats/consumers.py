import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from user_management.models import User
from teachers.models import Course
from asgiref.sync import sync_to_async
from .models import ChatMessage,CommunityChatMessages
from django.core.cache import cache
from datetime import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("TESTING CONNECTION AND REELS")
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.sender_id=self.scope['url_route']['kwargs']['id']
        self.room_group_name = f'chat_{self.room_name}'
        print(self.room_name)
        user_obj=await sync_to_async(User.objects.get)(pk=self.sender_id)
        print("user name is........",user_obj.username)
        self.sender_name=user_obj.username
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print(message)
        sender=await sync_to_async(User.objects.get)(pk=self.sender_id)
        print("sender is....",sender)
        community_chat=await sync_to_async(CommunityChatMessages.objects.create)(
            sender=sender,
            message=message,
            community=self.room_name
        )
        
        # send message to the room
        current_time = datetime.now().strftime("%H:%M")
        print(current_time)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type':'chat_message',
                'message':message,
                'sender':self.sender_id,
                'sender_name':self.sender_name,
                'timestamp':current_time

            }
        )
    async def chat_message(self,event):
        message=event['message']
        sender=event['sender']
        sender_name=event['sender_name']
        timestamp=event['timestamp']
        await self.send(text_data=json.dumps({
            'message':message,
            'sender': sender,
            'sender_name': sender_name,
            'timestamp':timestamp

        }))





class PersonalChatConsumers(AsyncWebsocketConsumer):
    async def connect(self):
        self.student_id=self.scope['url_route']['kwargs']['student_id']
        self.course_id=self.scope['url_route']['kwargs']['course_id']
        self.sender_id=self.scope['url_route']['kwargs']['sender_id']
        ids=sorted([int(self.student_id),int(self.course_id)])
        print(ids)
        self.room_group_name=f'chat_{ids[0]}-chat_{ids[1]}'
        print(self.room_group_name)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        await self.set_user_online(self.sender_id)
        await self.broadcast_user_status(self.sender_id, True)
    
    async def disconnect(self, code):
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.set_user_offline(self.sender_id)
        await self.broadcast_user_status(self.sender_id, False)
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print(message)
        sender=await sync_to_async(User.objects.get)(pk=self.sender_id)
        student=await sync_to_async(User.objects.get)(pk=self.student_id)
        course=await sync_to_async(Course.objects.get)(pk=self.course_id)
        print("sender is....",sender)
        print("student is....",student)
       
        

        chat_message = await sync_to_async(ChatMessage.objects.create)(
            sender=sender,
            student=student,
            message=message,
            course=course
        )

        # send message to the room
        current_time = datetime.now().strftime("%H:%M")
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type':'chat_message',
                'message':message,
                'sender_id': self.sender_id,
                'timestamp':current_time
            }
        )
    async def chat_message(self,event):
        message=event['message']
        sender_id = event['sender_id']
        timestamp=event['timestamp']
        print("curent time is..",timestamp)
        await self.send(text_data=json.dumps({
            'message':message,
            'sender_id': sender_id,
            'timestamp':timestamp
        }))

    @database_sync_to_async
    def set_user_online(self, user_id):
        cache.set(f'user_{user_id}_online', True, timeout=None)
    
    @database_sync_to_async
    def set_user_offline(self, user_id):
        cache.set(f'user_{user_id}_online', False, timeout=None)
    

    async def broadcast_user_status(self, user_id, is_online):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': user_id,
                'is_online': is_online
            }
        )

    async def user_status(self, event):
        user_id = event['user_id']
        is_online = event['is_online']
        
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'user_id': user_id,
            'is_online': is_online
        }))
    


