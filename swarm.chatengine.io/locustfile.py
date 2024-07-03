from locust import HttpUser, task, between

class BasicUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def ping_home(self):
        self.client.get("/")