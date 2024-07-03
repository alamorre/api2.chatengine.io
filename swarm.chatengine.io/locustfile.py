from locust import HttpUser, task, between
import itertools
import os

# Create an iterator to generate unique user names
user_iterator = itertools.count(1)

class BasicUser(HttpUser):
    wait_time = between(1, 10)
    chat_engine_project_id = os.getenv("CHAT_ENGINE_PROJECT_ID", "default_project_id")
    chat_engine_private_key = os.getenv("CHAT_ENGINE_PRIVATE_KEY", "default_private_key")

    def on_start(self):
        # Assign a unique name to each user
        self.user_num = next(user_iterator)
        self.user_name = f"user_{self.user_num}"
        self.create_chat_engine_user()

    def on_stop(self):
        # Cleanup process to delete the user
        self.delete_chat_engine_user()

    @task
    def handle_chat(self):
        if not hasattr(self, 'chat_id'):
            self.create_chat()
        else:
            self.fetch_chat()

    def create_chat(self):
        if hasattr(self, 'user_id'):
            url = f"{self.host}/chats/"
            headers = {
                "Project-ID": self.chat_engine_project_id,
                "User-Name": self.user_name,
                "User-Secret": self.user_name
            }
            data = {
                "title": f"Chat for {self.user_name}",
                "usernames": [self.user_name],  # Add this user to the chat
            }
            with self.client.post(url, json=data, headers=headers, catch_response=True) as response:
                print('Create chat', response.status_code)
                if response.status_code == 201:
                    self.chat_id = response.json().get("id")
                    print(f"Chat created successfully for {self.user_name} with Chat ID {self.chat_id}.")
                else:
                    response.failure(f"Failed to create chat for {self.user_name}: {response.status_code}, {response.text}")
        else:
            print(f"No user ID found for {self.user_name}. Chat creation skipped.")

    def fetch_chat(self):
        if hasattr(self, 'chat_id'):
            url = f"{self.host}/chats/{self.chat_id}/"
            headers = {
                "Project-ID": self.chat_engine_project_id,
                "User-Name": self.user_name,
                "User-Secret": self.user_name
            }
            with self.client.get(url, headers=headers, catch_response=True) as response:
                print('Fetch chat', response.status_code)
                if response.status_code == 200:
                    print(f"Fetched chat data for {self.user_name} with Chat ID {self.chat_id}.")
                else:
                    response.failure(f"Failed to fetch chat data for {self.user_name}: {response.status_code}, {response.text}")
        else:
            print(f"No chat ID found for {self.user_name}. Fetch skipped.")

    def create_chat_engine_user(self):
        url = f"{self.host}/users/"
        headers = {
            "Project-ID": self.chat_engine_project_id,
            "Private-Key": self.chat_engine_private_key,
            "Content-Type": "application/json"
        }
        data = {
            "username": self.user_name,
            "secret": self.user_name,  # You can use any string as the secret
            "email": f"{self.user_name}@example.com",  # Optional
            "first_name": "Test",  # Optional
            "last_name": "User"  # Optional
        }
        with self.client.post(url, json=data, headers=headers, catch_response=True) as response:
            if response.status_code == 201:
                self.user_id = response.json().get("id")
                print(f"User {self.user_name} created successfully with ID {self.user_id}.")
            else:
                response.failure(f"Failed to create user {self.user_name}: {response.status_code}, {response.text}")

    def delete_chat_engine_user(self):
        if hasattr(self, 'user_id'):
            url = f"{self.host}/users/{self.user_id}/"
            headers = {
                "Project-ID": self.chat_engine_project_id,
                "Private-Key": self.chat_engine_private_key
            }
            with self.client.delete(url, headers=headers, catch_response=True) as response:
                if response.status_code == 200:
                    print(f"User {self.user_name} deleted successfully.")
                else:
                    response.failure(f"Failed to delete user {self.user_name}: {response.status_code}, {response.text}")
        else:
            print(f"No user ID found for {self.user_name}. Deletion skipped.")
