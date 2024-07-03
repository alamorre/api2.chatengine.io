import json 

from server.redis import redis_pubsub
from chats.models import ChatPerson

def get_people_ids_in_chat(chat_id):
        chat_people = ChatPerson.objects.filter(chat=chat_id)
        return [chat_person.person_id for chat_person in chat_people]

class ChatPublisher:
    def __init__(self):
        pass

    @staticmethod
    def publish_chat_data(action, chat_data, people_ids=None):
        if people_ids is None:
            people_ids = get_people_ids_in_chat(chat_id=chat_data['id'])

        message = json.dumps({"action": action, "data": chat_data})

        for person_id in people_ids:
            print(f"Publishing to person:{str(person_id)}")
            result = redis_pubsub.publish(f"person:{str(person_id)}", message)
            print(f"Published to person:{str(person_id)}: {result}")

        redis_pubsub.publish(f"chat:{str(chat_data['id'])}", message)

    @staticmethod
    def publish_message_data(action, chat, message_data, people_ids=None):
        if people_ids is None:
            people_ids = get_people_ids_in_chat(chat_id=chat.id)
        
        data = {"id": chat.pk, "message": message_data}
        message = json.dumps({"action": action, "data": data})

        for person_id in people_ids:
            print(f"Publishing to person:{str(person_id)}")
            result = redis_pubsub.publish(f"person:{str(person_id)}", message)
            print(f"Published to person:{str(person_id)}: {result}")
        
        redis_pubsub.publish(f"chat:{str(chat.pk)}", message)

chat_publisher = ChatPublisher()
