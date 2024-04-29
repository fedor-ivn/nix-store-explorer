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
    token = None

    def on_start(self):
        with self.client.post("/auth/register", json=USER_1, catch_response=True) as response:
            if response.status_code not in [201, 400]:
                response.failure("Unexpected error")
            response.success()

        response = self.client.post(
            "/auth/jwt/login",
            data={"username": USER_1["email"], "password": USER_1["password"]},
        )
        self.token = response.cookies["fastapiusersauth"]

    @task
    def create_store(self):
        with self.client.post("/store/store", cookies={"fastapiusersauth": self.token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        with self.client.delete("/store/store", cookies={"fastapiusersauth": self.token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

    @task
    def get_all_stores(self):
        with self.client.post("/store/store", cookies={"fastapiusersauth": self.token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        self.client.get("/store", cookies={"fastapiusersauth": self.token})

        with self.client.delete("/store/store", cookies={"fastapiusersauth": self.token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

    @task
    def get_specific_store(self):
        with self.client.post("/store/store", cookies={"fastapiusersauth": self.token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        with self.client.get("/store/store", cookies={"fastapiusersauth": self.token}, catch_response=True) as response:
            if response.status_code not in [200, 404]:
                response.failure("Unexpected error")
            response.success()

        with self.client.delete("/store/store", cookies={"fastapiusersauth": self.token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

    @task
    def work_with_package(self):
        with self.client.post("/store/store", cookies={"fastapiusersauth": self.token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        with self.client.post("/store/store/package/python3",
                              cookies={"fastapiusersauth": self.token},
                              catch_response=True) as response:
            if response.status_code not in [200, 404]:
                response.failure("Unexpected error")
            response.success()

        with self.client.delete("/store/store/package/python3",
                              cookies={"fastapiusersauth": self.token},
                              catch_response=True) as response:
            if response.status_code not in [200, 404]:
                response.failure("Unexpected error")
            response.success()

        with self.client.delete("/store/store", cookies={"fastapiusersauth": self.token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

    @task
    def get_paths_difference(self):
        with self.client.post("/store/store1", cookies={"fastapiusersauth": self.token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        with self.client.post("/store/store1/package/python3",
                              cookies={"fastapiusersauth": self.token},
                              catch_response=True) as response:
            if response.status_code not in [200, 404]:
                response.failure("Unexpected error")
            response.success()

        with self.client.post("/store/store2", cookies={"fastapiusersauth": self.token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        with self.client.post("/store/store2/package/neovim",
                                cookies={"fastapiusersauth": self.token},
                                catch_response=True) as response:
            if response.status_code not in [200, 404]:
                response.failure("Unexpected error")
            response.success()

        with self.client.get("/store/store1/difference/store_2",
                             cookies={"fastapiusersauth": self.token},
                             catch_response=True) as response:
            if response.status_code not in [200, 404]:
                response.failure("Unexpected error")
            response.success()

        with self.client.delete("/store/store1", cookies={"fastapiusersauth": self.token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        with self.client.delete("/store/store2", cookies={"fastapiusersauth": self.token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

    @task
    def get_closures_difference(self):
        with self.client.post("/store/store1", cookies={"fastapiusersauth": self.token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        with self.client.post("/store/store1/package/python3",
                              cookies={"fastapiusersauth": self.token},
                              catch_response=True) as response:
            if response.status_code not in [200, 404]:
                response.failure("Unexpected error")
            response.success()

        with self.client.post("/store/store2", cookies={"fastapiusersauth": self.token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        with self.client.post("/store/store2/package/neovim",
                                cookies={"fastapiusersauth": self.token},
                                catch_response=True) as response:
            if response.status_code not in [200, 404]:
                response.failure("Unexpected error")
            response.success()

        with self.client.get("/store/store1/package/python3/closure-difference/store2/neovim",
                             cookies={"fastapiusersauth": self.token},
                             catch_response=True) as response:
            if response.status_code not in [200, 404]:
                response.failure("Unexpected error")
            response.success()

        with self.client.delete("/store/store1", cookies={"fastapiusersauth": self.token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        with self.client.delete("/store/store2", cookies={"fastapiusersauth": self.token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

    @task
    def get_package_meta(self):
        with self.client.post("/store/store1", cookies={"fastapiusersauth": self.token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        with self.client.get("/store/store2/package/neovim",
                                cookies={"fastapiusersauth": self.token},
                                catch_response=True) as response:
            if response.status_code not in [200, 404]:
                response.failure("Unexpected error")
            response.success()

        with self.client.delete("/store/store1", cookies={"fastapiusersauth": self.token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()
