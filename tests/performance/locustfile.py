from uuid import uuid4

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
    # min_wait = 1000
    # max_wait = 1000
    #
    # def wait_time(self):
    #     return 0.1

    # @task(1)
    # def register_users(self):
    #     r = self.client.post(
    #         "/auth/register",
    #         json=USER_1,
    #     )
    #
    #     self.client.post(
    #         "/auth/register",
    #         json=USER_2,
    #     )

    @task
    def create_store(self):
        response = self.client.post(
            "/auth/jwt/login",
            data={"username": USER_1["email"], "password": USER_1["password"]},
        )
        token = response.cookies["fastapiusersauth"]

        with self.client.post("/store/store", cookies={"fastapiusersauth": token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        with self.client.delete("/store/store", cookies={"fastapiusersauth": token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

    @task
    def get_all_stores(self):
        response = self.client.post(
            "/auth/jwt/login",
            data={"username": USER_1["email"], "password": USER_1["password"]},
        )
        token = response.cookies["fastapiusersauth"]

        with self.client.post("/store/store", cookies={"fastapiusersauth": token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        self.client.get("/store", cookies={"fastapiusersauth": token})

        with self.client.delete("/store/store", cookies={"fastapiusersauth": token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

    @task
    def get_specific_store(self):
        response = self.client.post(
            "/auth/jwt/login",
            data={"username": USER_1["email"], "password": USER_1["password"]},
        )
        token = response.cookies["fastapiusersauth"]

        with self.client.post("/store/store", cookies={"fastapiusersauth": token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        with self.client.get("/store/store", cookies={"fastapiusersauth": token}, catch_response=True) as response:
            if response.status_code not in [200, 404]:
                response.failure("Unexpected error")
            response.success()

        with self.client.delete("/store/store", cookies={"fastapiusersauth": token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

    @task
    def work_with_package(self):
        response = self.client.post(
            "/auth/jwt/login",
            data={"username": USER_1["email"], "password": USER_1["password"]},
        )
        token = response.cookies["fastapiusersauth"]

        with self.client.post("/store/store", cookies={"fastapiusersauth": token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        with self.client.post("/store/store/package/python3",
                              cookies={"fastapiusersauth": token},
                              catch_response=True) as response:
            if response.status_code not in [200, 404]:
                response.failure("Unexpected error")
            response.success()

        with self.client.delete("/store/store/package/python3",
                              cookies={"fastapiusersauth": token},
                              catch_response=True) as response:
            if response.status_code not in [200, 404]:
                response.failure("Unexpected error")
            response.success()

        with self.client.delete("/store/store", cookies={"fastapiusersauth": token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

    @task
    def get_paths_difference(self):
        response = self.client.post(
            "/auth/jwt/login",
            data={"username": USER_1["email"], "password": USER_1["password"]},
        )
        token = response.cookies["fastapiusersauth"]

        with self.client.post("/store/store1", cookies={"fastapiusersauth": token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        with self.client.post("/store/store1/package/python3",
                              cookies={"fastapiusersauth": token},
                              catch_response=True) as response:
            if response.status_code not in [200, 404]:
                response.failure("Unexpected error")
            response.success()

        with self.client.post("/store/store2", cookies={"fastapiusersauth": token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        with self.client.post("/store/store2/package/neovim",
                                cookies={"fastapiusersauth": token},
                                catch_response=True) as response:
            if response.status_code not in [200, 404]:
                response.failure("Unexpected error")
            response.success()

        with self.client.get("/store/store1/difference/store_2",
                             cookies={"fastapiusersauth": token},
                             catch_response=True) as response:
            if response.status_code not in [200, 404]:
                response.failure("Unexpected error")
            response.success()

        with self.client.delete("/store/store1", cookies={"fastapiusersauth": token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        with self.client.delete("/store/store2", cookies={"fastapiusersauth": token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

    @task
    def get_closures_difference(self):
        response = self.client.post(
            "/auth/jwt/login",
            data={"username": USER_1["email"], "password": USER_1["password"]},
        )
        token = response.cookies["fastapiusersauth"]

        with self.client.post("/store/store1", cookies={"fastapiusersauth": token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        with self.client.post("/store/store1/package/python3",
                              cookies={"fastapiusersauth": token},
                              catch_response=True) as response:
            if response.status_code not in [200, 404]:
                response.failure("Unexpected error")
            response.success()

        with self.client.post("/store/store2", cookies={"fastapiusersauth": token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        with self.client.post("/store/store2/package/neovim",
                                cookies={"fastapiusersauth": token},
                                catch_response=True) as response:
            if response.status_code not in [200, 404]:
                response.failure("Unexpected error")
            response.success()

        with self.client.get("/store/store1/package/python3/closure-difference/store2/neovim",
                             cookies={"fastapiusersauth": token},
                             catch_response=True) as response:
            if response.status_code not in [200, 404]:
                response.failure("Unexpected error")
            response.success()

        with self.client.delete("/store/store1", cookies={"fastapiusersauth": token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        with self.client.delete("/store/store2", cookies={"fastapiusersauth": token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

    @task
    def get_package_meta(self):
        response = self.client.post(
            "/auth/jwt/login",
            data={"username": USER_1["email"], "password": USER_1["password"]},
        )
        token = response.cookies["fastapiusersauth"]

        with self.client.post("/store/store1", cookies={"fastapiusersauth": token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()

        with self.client.get("/store/store2/package/neovim",
                                cookies={"fastapiusersauth": token},
                                catch_response=True) as response:
            if response.status_code not in [200, 404]:
                response.failure("Unexpected error")
            response.success()

        with self.client.delete("/store/store1", cookies={"fastapiusersauth": token}, catch_response=True) as response:
            if response.status_code not in [200, 400]:
                response.failure("Unexpected error")
            response.success()
