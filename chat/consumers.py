# from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from src.models import RegisterUser
from .models import Message, ChatRoom
from src.fcm_notification import send_another, send_to_one
from .views import get_last_10_messages, get_user_contact, get_current_chat
from adminpanel.models import User

# User = RegisterUser()

CONNECTED = False


class ChatRoomConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        print('-------------------- ROOM GROUP NAME', self.room_group_name)
        # Join room group
        # count = getattr(self.channel_layer, self.room_group_name, 0)
        c = len(self.channel_layer.groups.get(self.room_group_name, {}).items())
        print(self.channel_layer.groups.get(self.room_group_name))
        print(self.channel_layer.groups.get(self.room_name))
        print(self.channel_layer.groups.get(self.room_group_name, {}))
        print(self.channel_layer.groups.get(self.room_group_name, {}).items())
        print([x for x in self.channel_layer.groups])
        print('CONNECTED USERS-----', c)
        if c > 0:
            global CONNECTED
            CONNECTED = True
            print('-------------inside connect method', CONNECTED)
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        global CONNECTED
        CONNECTED = False
        print('-------------Inside disconnect', CONNECTED)
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        print('-----------------', text_data)
        text_data_json = json.loads(text_data)
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', text_data_json)
        print('----------inside receive', CONNECTED)
        message = text_data_json['message']
        try:
            try:
                print('inside nested try-----')
                chat1 = ChatRoom.objects.get(sender=RegisterUser.objects.get(id=text_data_json['sender']),
                                             receiver=RegisterUser.objects.get(id=text_data_json['receiver']))
                room = ChatRoom.objects.get(id=chat1.id)
                print(room.id)
                sender = RegisterUser.objects.get(id=text_data_json['sender'])
                receiver = RegisterUser.objects.get(id=text_data_json['receiver'])
                m = Message.objects.create(
                    sender=sender,
                    receiver=receiver,
                    message=text_data_json['message'],
                    is_image=text_data_json['is_image']
                )
                chat1.messages.add(m)
                # try:
                #     first_name = sender.first_name
                #     email = receiver.email
                #     user = User.objects.get(email=email)
                #     fcm_token = user.device_token
                #     print('FCM TOKEN', fcm_token)
                #     print(email)
                #     print(first_name)
                #     # global CONNECTED
                #     if CONNECTED:
                #         print('DATA MESSAGE_____________________', CONNECTED)
                #         data_message = {
                #             "body": text_data_json['message'],
                #             "title": first_name,
                #             "is_image": str(text_data_json['is_image']),
                #             "room_id": chat1.id
                #         }
                #         respo = send_to_one(fcm_token, data_message)
                #         print(respo)
                #     else:
                #         print('NOTIFICATION MESSAGE____________', CONNECTED)
                #         body = ''
                #         if text_data_json['is_image']:
                #             title = first_name
                #             body = 'Image'
                #             # message_type = data_message
                #             respo = send_another(fcm_token, title, body)
                #             print(respo)
                #         else:
                #             title = first_name
                #             body = text_data_json['message']
                #             # message_type = data_message
                #             respo = send_another(fcm_token, title, body)
                #             print(respo)
                # except Exception as e:
                #     print('Inside fcm exception', e)
                #     pass
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': text_data_json['message'],
                        'sender': text_data_json['sender'],
                        'receiver': text_data_json['receiver'],
                        'is_image': text_data_json['is_image'],
                        'm': m
                    }
                )
                try:
                    first_name = sender.first_name
                    email = receiver.email
                    user = User.objects.get(email=email)
                    fcm_token = user.device_token
                    print('FCM TOKEN', fcm_token)
                    print(email)
                    print(first_name)
                    # global CONNECTED
                    if CONNECTED:
                        print('DATA MESSAGE_____________________', CONNECTED)
                        data_message = {
                            "body": text_data_json['message'],
                            "title": first_name,
                            "is_image": str(text_data_json['is_image']),
                            "room_id": chat1.id
                        }
                        respo = send_to_one(fcm_token, data_message)
                        print(respo)
                    else:
                        print('NOTIFICATION MESSAGE____________', CONNECTED)
                        body = ''
                        if text_data_json['is_image']:
                            title = first_name
                            body = 'Image'
                            # message_type = data_message
                            respo = send_another(fcm_token, title, body)
                            print(respo)
                        else:
                            title = first_name
                            body = text_data_json['message']
                            # message_type = data_message
                            respo = send_another(fcm_token, title, body)
                            print(respo)
                except Exception as e:
                    print('Inside fcm exception', e)
                    pass

            except Exception as e:
                print('inside nested except', e)
                chat1 = ChatRoom.objects.get(sender=RegisterUser.objects.get(id=text_data_json['receiver']),
                                             receiver=RegisterUser.objects.get(id=text_data_json['sender']))
                print('----', chat1.id)
                sender = RegisterUser.objects.get(id=text_data_json['sender'])
                receiver = RegisterUser.objects.get(id=text_data_json['receiver'])
                m = Message.objects.create(
                    sender=sender,
                    receiver=receiver,
                    message=text_data_json['message'],
                    is_image=text_data_json['is_image']
                )
                chat1.messages.add(m)
                # try:
                #     email = receiver.email
                #     first_name = sender.first_name
                #     user = User.objects.get(email=email)
                #     fcm_token = user.device_token
                #     print('FCM TOKEN ', fcm_token)
                #     print(email)
                #     # global CONNECTED
                #     if CONNECTED:
                #         print('DATA MESSAGE______________', CONNECTED)
                #         data_message = {
                #             "body": text_data_json['message'],
                #             "title": first_name,
                #             "is_image": str(text_data_json['is_image']),
                #             "room_id": chat1.id
                #         }
                #         respo = send_to_one(fcm_token, data_message)
                #         print(respo)
                #     else:
                #         print('NOTIFICATION_____________', CONNECTED)
                #         if text_data_json['is_image']:
                #             title = first_name
                #             body = 'Image'
                #             # message_type = data_message
                #             respo = send_another(fcm_token, title, body)
                #             print(respo)
                #         else:
                #             title = first_name
                #             body = text_data_json['message']
                #             # message_type = data_message
                #             respo = send_another(fcm_token, title, body)
                #             print(respo)
                # except Exception as e:
                #     print('inside FCM EXCEPTION', e)
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': text_data_json['message'],
                        'sender': text_data_json['receiver'],
                        'receiver': text_data_json['sender'],
                        'is_image': text_data_json['is_image'],
                        'm': m,
                    }
                )
                try:
                    email = receiver.email
                    first_name = sender.first_name
                    user = User.objects.get(email=email)
                    fcm_token = user.device_token
                    print('FCM TOKEN ', fcm_token)
                    print(email)
                    # global CONNECTED
                    if CONNECTED:
                        print('DATA MESSAGE______________', CONNECTED)
                        data_message = {
                            "body": text_data_json['message'],
                            "title": first_name,
                            "is_image": str(text_data_json['is_image']),
                            "room_id": chat1.id
                        }
                        respo = send_to_one(fcm_token, data_message)
                        print(respo)
                    else:
                        print('NOTIFICATION_____________', CONNECTED)
                        if text_data_json['is_image']:
                            title = first_name
                            body = 'Image'
                            # message_type = data_message
                            respo = send_another(fcm_token, title, body)
                            print(respo)
                        else:
                            title = first_name
                            body = text_data_json['message']
                            # message_type = data_message
                            respo = send_another(fcm_token, title, body)
                            print(respo)
                except Exception as e:
                    print('inside FCM EXCEPTION', e)

        except Exception as e:
            print('inside outer except', e)
            x = ChatRoom.objects.create(sender=RegisterUser.objects.get(id=text_data_json['sender']),
                                        receiver=RegisterUser.objects.get(id=text_data_json['receiver']))
            sender = RegisterUser.objects.get(id=text_data_json['sender'])
            receiver = RegisterUser.objects.get(id=text_data_json['receiver'])
            m = Message.objects.create(
                sender=sender,
                receiver=receiver,
                message=text_data_json['message'],
                is_image=text_data_json['is_image']
            )
            x.messages.add(m)
            # try:
            #     email = RegisterUser.objects.get(id=text_data_json['receiver']).email
            #     first_name = RegisterUser.objects.get(id=text_data_json['sender']).first_name
            #     user = User.objects.get(email=email)
            #     fcm_token = user.device_token
            #     print('FCM TOKEN ', fcm_token)
            #     print(x.id)
            #     print(email)
            #     # global CONNECTED
            #     if CONNECTED:
            #         print('DATA MESSAGE____________', CONNECTED)
            #         data_message = {
            #             "body": text_data_json['message'],
            #             "title": first_name,
            #             "is_image": str(text_data_json['is_image']),
            #             "room_id": x.id
            #         }
            #         respo = send_to_one(fcm_token, data_message)
            #         print(respo)
            #     else:
            #         print('NOTIFICATION_____________', CONNECTED)
            #         body = ''
            #         if text_data_json['is_image']:
            #             title = first_name
            #             body = 'Image'
            #             # message_type = data_message
            #             respo = send_another(fcm_token, title, body)
            #             print(respo)
            #         else:
            #             title = first_name
            #             body = text_data_json['message']
            #             # message_type = data_message
            #             respo = send_another(fcm_token, title, body)
            #             print(respo)
            # except Exception as e:
            #     print('INSIDE FCM EXCEPTION', e)
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': text_data_json['message'],
                    'sender': text_data_json['sender'],
                    'receiver': text_data_json['receiver'],
                    'is_image': text_data_json['is_image'],
                    'm': m
                }
            )
            try:
                email = RegisterUser.objects.get(id=text_data_json['receiver']).email
                first_name = RegisterUser.objects.get(id=text_data_json['sender']).first_name
                user = User.objects.get(email=email)
                fcm_token = user.device_token
                print('FCM TOKEN ', fcm_token)
                print(x.id)
                print(email)
                # global CONNECTED
                if CONNECTED:
                    print('DATA MESSAGE____________', CONNECTED)
                    data_message = {
                        "body": text_data_json['message'],
                        "title": first_name,
                        "is_image": str(text_data_json['is_image']),
                        "room_id": x.id
                    }
                    respo = send_to_one(fcm_token, data_message)
                    print(respo)
                else:
                    print('NOTIFICATION_____________', CONNECTED)
                    body = ''
                    if text_data_json['is_image']:
                        title = first_name
                        body = 'Image'
                        # message_type = data_message
                        respo = send_another(fcm_token, title, body)
                        print(respo)
                    else:
                        title = first_name
                        body = text_data_json['message']
                        # message_type = data_message
                        respo = send_another(fcm_token, title, body)
                        print(respo)
            except Exception as e:
                print('INSIDE FCM EXCEPTION', e)

    # Receive message from room group
    def chat_message(self, event):
        print('inside send', event)
        # message = event['message']
        # print(message)
        # Send message to WebSocket
        # self.channel_layer.group_send(
        #     text_data=json.dumps({
        #         'sender': event['sender'],
        #         'receiver': event['receiver'],
        #         'message': message
        #     }))
        message_sender_obj = event['m'].sender
        message_receiver_obj = event['m'].receiver
        message_content = event['m'].message
        print('Message---->>>', message_sender_obj, message_receiver_obj, message_content, event['m'].id)
        self.send(
            text_data=json.dumps({
                "sender": event['m'].sender.id,
                "receiver": event['m'].receiver.id,
                "message": event['m'].message,
                "is_image": event['m'].is_image,
                "id": event['m'].id,
                "created_at": str(event['m'].created_at.replace(microsecond=0)),
                "cleared_by": str(event['m'].cleared_by)
                # 'sender': event['m'],
                # 'receiver': event['receiver'],
                # 'message': event['message']
            }))

        # class ChatConsumer(WebsocketConsumer):
        #
        #     def fetch_messages(self, data):
        #         messages = get_last_10_messages(data['chatId'])
        #         content = {
        #             'command': 'messages',
        #             'messages': self.messages_to_json(messages)
        #         }
        #         self.send_message(content)
        #
        #     def new_message(self, data):
        #         user_contact = get_user_contact(data['from'])
        #         message = Message.objects.create(
        #             contact=user_contact,
        #             content=data['message'])
        #         current_chat = get_current_chat(data['chatId'])
        #         current_chat.messages.add(message)
        #         current_chat.save()
        #         content = {
        #             'command': 'new_message',
        #             'message': self.message_to_json(message)
        #         }
        #         return self.send_chat_message(content)
        #
        #     def messages_to_json(self, messages):
        #         result = []
        #         for message in messages:
        #             result.append(self.message_to_json(message))
        #         return result
        #
        #     def message_to_json(self, message):
        #         return {
        #             'id': message.id,
        #             'author': message.contact.user.first_name,
        #             'content': message.content,
        #             'timestamp': str(message.timestamp)
        #         }
        #
        #     commands = {
        #         'fetch_messages': fetch_messages,
        #         'new_message': new_message
        #     }
        #
        #     def connect(self):
        #         self.room_name = self.scope['url_route']['kwargs']['room_name']
        #         self.room_group_name = 'chat_%s' % self.room_name
        #         async_to_sync(self.channel_layer.group_add)(
        #             self.room_group_name,
        #             self.channel_name
        #         )
        #         self.accept()
        #
        #     def disconnect(self, close_code):
        #         async_to_sync(self.channel_layer.group_discard)(
        #             self.room_group_name,
        #             self.channel_name
        #         )
        #
        #     def receive(self, text_data):
        #         data = json.loads(text_data)
        #         self.commands[data['command']](self, data)
        #
        #     def send_chat_message(self, message):
        #         async_to_sync(self.channel_layer.group_send)(
        #             self.room_group_name,
        #             {
        #                 'type': 'chat_message',
        #                 'message': message
        #             }
        #         )
        #
        #     def send_message(self, message):
        #         self.send(text_data=json.dumps(message))
        #
        #     def chat_message(self, event):
        #         message = event['message']
        #         self.send(text_data=json.dumps(message))
