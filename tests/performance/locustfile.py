from locust import HttpUser, task

USER_1 = {
    "email": "user1@example.com",
    "password": "string",
    "is_active": True,
    "is_superuser": False,
    "is_verified": False,
}

USER_2 = {
    "email": "user2@example.com",
    "password": "string",
    "is_active": True,
    "is_superuser": False,
    "is_verified": False,
}


class MyUser(HttpUser):
    min_wait = 1000
    max_wait = 1000

    def wait_time(self):
        return 0.1

    @task(1)
    def register_users(self):
        self.client.post(
            "/auth/register",
            json=USER_1,
        )

        self.client.post(
            "/auth/register",
            json=USER_2,
        )

    @task(2)
    def create_store(self):
        response = self.client.post(
            "/auth/jwt/login",
            data={"username": USER_1["email"], "password": USER_1["password"]},
        )
        token = response.cookies["fastapiusersauth"]
        self.client.post("/store/store", cookies={"fastapiusersauth": token})

    @task(3)
    def get_all_stores(self):
        response = self.client.post(
            "/auth/jwt/login",
            data={"username": USER_2["email"], "password": USER_2["password"]},
        )
        token = response.cookies["fastapiusersauth"]
        self.client.get("/store", cookies={"fastapiusersauth": token})
