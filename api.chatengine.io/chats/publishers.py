from server.redis import redis_client
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

        for person_id in people_ids:
            redis_client.publish(
                f"person:{str(person_id)}",
                {"type": "dispatch_data", "action": action, "data": chat_data}
            )
        
        redis_client.publish(
            f"chat:{str(chat_data['id'])}",
            {"type": "dispatch_data", "action": action, "data": chat_data}
        )

    @staticmethod
    def publish_message_data(action, chat, message_data, people_ids=None):
        if people_ids is None:
            people_ids = get_people_ids_in_chat(chat_id=chat.id)
        
        data = {"id": chat.pk, "message": message_data}

        for person_id in people_ids:
            redis_client.publish(
                f"person:{str(person_id)}",
                {"type": "dispatch_data", "action": action, "data": data}
            )
        
        redis_client.publish(
            f"chat:{str(chat.pk)}",
            {"type": "dispatch_data", "action": action, "data": data}
        )

chat_publisher = ChatPublisher()
