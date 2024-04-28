from contextlib import ExitStack
from unittest.mock import call, patch

from src.frontend import TIMEOUT, base_url, login_page, logout, main_page, register_page


def test_register_page_success():
    with ExitStack() as stack:
        mock_post = stack.enter_context(patch("src.frontend.requests.post"))
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_text_input = stack.enter_context(patch("src.frontend.st.text_input"))
        mock_success = stack.enter_context(patch("src.frontend.st.success"))

        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"status": "success"}

        mock_button.return_value = True
        mock_text_input.side_effect = ["user@example.com", "password"]

        register_page()

        mock_post.assert_called_once_with(
            f"{base_url}/auth/register",
            json={
                "email": "user@example.com",
                "password": "password",
                "is_active": True,
                "is_superuser": False,
                "is_verified": False,
            },
            timeout=TIMEOUT,
        )
        mock_success.assert_called_once_with("Registration successful")


def test_register_page_failure():
    with ExitStack() as stack:
        mock_post = stack.enter_context(patch("src.frontend.requests.post"))
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_text_input = stack.enter_context(patch("src.frontend.st.text_input"))
        mock_error = stack.enter_context(patch("src.frontend.st.error"))

        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {"detail": "error"}

        mock_button.return_value = True
        mock_text_input.side_effect = ["user@example.com", "password"]

        register_page()

        mock_post.assert_called_once_with(
            f"{base_url}/auth/register",
            json={
                "email": "user@example.com",
                "password": "password",
                "is_active": True,
                "is_superuser": False,
                "is_verified": False,
            },
            timeout=TIMEOUT,
        )
        mock_error.assert_called_once_with("Registration failed")


def test_login_page_success():
    with ExitStack() as stack:
        mock_post = stack.enter_context(patch("src.frontend.requests.post"))
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_text_input = stack.enter_context(patch("src.frontend.st.text_input"))
        mock_success = stack.enter_context(patch("src.frontend.st.success"))
        mock_session_state = stack.enter_context(patch("src.frontend.st.session_state"))
        mock_post.return_value.status_code = 204
        mock_post.return_value.cookies = {"fastapiusersauth": "token"}

        mock_button.return_value = True
        mock_text_input.side_effect = ["user@example.com", "password"]

        login_page()

        mock_post.assert_called_once_with(
            f"{base_url}/auth/jwt/login",
            data={"username": "user@example.com", "password": "password"},
            timeout=TIMEOUT,
        )

        print(mock_session_state.__setitem__.call_args_list)
        mock_success.assert_called_once_with("Login successful")
        mock_session_state.__setitem__.assert_called_with(
            "Set_cookies", {"fastapiusersauth": "token"}
        )
        assert mock_session_state.is_authorized is True


def test_login_page_failure():
    with ExitStack() as stack:
        mock_post = stack.enter_context(patch("src.frontend.requests.post"))
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_text_input = stack.enter_context(patch("src.frontend.st.text_input"))
        mock_error = stack.enter_context(patch("src.frontend.st.error"))

        mock_post.return_value.status_code = 401
        mock_post.return_value.json.return_value = {"detail": "error"}
        mock_button.return_value = True
        mock_text_input.side_effect = ["user@example.com", "password"]

        login_page()

        mock_post.assert_called_once_with(
            f"{base_url}/auth/jwt/login",
            data={"username": "user@example.com", "password": "password"},
            timeout=TIMEOUT,
        )

        mock_error.assert_called_once_with(
            "Login failed. Please check your credentials."
        )


def test_logout_page():
    with ExitStack() as stack:
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_success = stack.enter_context(patch("src.frontend.st.success"))
        mock_post = stack.enter_context(patch("src.frontend.requests.post"))
        mock_cookie_manager = stack.enter_context(patch("src.frontend.cookie_manager"))
        mock_session_state = stack.enter_context(patch("src.frontend.st.session_state"))

        mock_button.return_value = True
        mock_post.return_value.status_code = 204
        mock_session_state.__getitem__.return_value = {"fastapiusersauth": "token"}

        logout()

        assert mock_session_state.is_authorized is False
        mock_success.assert_called_once_with("Logout successful")
        mock_post.assert_called_once_with(
            f"{base_url}/auth/jwt/logout",
            cookies={"fastapiusersauth": "token"},
            timeout=TIMEOUT,
        )
        mock_cookie_manager.delete.assert_called_once_with("fastapiusersauth")


def test_logout_page_failure():
    with ExitStack() as stack:
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_error = stack.enter_context(patch("src.frontend.st.error"))
        mock_post = stack.enter_context(patch("src.frontend.requests.post"))
        mock_session_state = stack.enter_context(patch("src.frontend.st.session_state"))

        mock_button.return_value = True
        mock_post.return_value.status_code = 401
        mock_session_state.__getitem__.return_value = {"fastapiusersauth": "token"}

        logout()

        mock_error.assert_called_once_with("Logout failed")


def test_main_page_create_store():
    def button_side_effect(*args, **kwargs):
        if args[0] == "Create store":
            return True
        return False

    def text_input_side_effect(*args, **kwargs):
        return "store_name"

    with ExitStack() as stack:
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_success = stack.enter_context(patch("src.frontend.st.success"))
        mock_post = stack.enter_context(patch("src.frontend.requests.post"))
        mock_session_state = stack.enter_context(patch("src.frontend.st.session_state"))
        mock_text_input = stack.enter_context(patch("src.frontend.st.text_input"))

        mock_button.side_effect = button_side_effect
        mock_post.return_value.status_code = 200
        cookies = {"fastapiusersauth", "token"}
        mock_session_state.__getitem__.return_value = cookies
        mock_text_input.side_effect = text_input_side_effect

        main_page()

        mock_post.assert_called_once_with(
            f"{base_url}/store/store_name",
            cookies=cookies,
            timeout=TIMEOUT,
        )
        mock_success.assert_called_once_with("Store created successfully!")


def test_main_page_create_store_failure():
    def button_side_effect(*args, **kwargs):
        if args[0] == "Create store":
            return True
        return False

    def text_input_side_effect(*args, **kwargs):
        return "store_name"

    with ExitStack() as stack:
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_error = stack.enter_context(patch("src.frontend.st.error"))
        mock_post = stack.enter_context(patch("src.frontend.requests.post"))
        mock_session_state = stack.enter_context(patch("src.frontend.st.session_state"))
        mock_text_input = stack.enter_context(patch("src.frontend.st.text_input"))

        mock_button.side_effect = button_side_effect
        mock_post.return_value.status_code = 400
        cookies = {"fastapiusersauth", "token"}
        mock_session_state.__getitem__.return_value = cookies
        mock_text_input.side_effect = text_input_side_effect

        main_page()

        mock_post.assert_called_once_with(
            f"{base_url}/store/store_name", cookies=cookies, timeout=TIMEOUT
        )
        mock_error.assert_called_once_with("Failed to create store")


def test_main_page_get_store():
    def button_side_effect(*args, **kwargs):
        if args[0] == "Get store":
            return True
        return False

    def text_input_side_effect(*args, **kwargs):
        return "store_name"

    with ExitStack() as stack:
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_write = stack.enter_context(patch("src.frontend.st.write"))
        mock_get = stack.enter_context(patch("src.frontend.requests.get"))
        mock_session_state = stack.enter_context(patch("src.frontend.st.session_state"))
        mock_text_input = stack.enter_context(patch("src.frontend.st.text_input"))

        mock_button.side_effect = button_side_effect
        mock_get.return_value.status_code = 200
        store_data = {"id": 1, "name": "store_name", "owner_id": 1}
        mock_get.return_value.json.return_value = store_data
        cookies = {"fastapiusersauth", "token"}
        mock_session_state.__getitem__.return_value = cookies
        mock_text_input.side_effect = text_input_side_effect

        main_page()

        mock_get.assert_called_once_with(
            f"{base_url}/store/store_name", cookies=cookies, timeout=TIMEOUT
        )
        calls = [
            call("Store ID: 1"),
            call("Store name: store_name"),
            call("Owner ID: 1"),
        ]
        mock_write.assert_has_calls(calls)


def test_main_page_get_store_failure():
    def button_side_effect(*args, **kwargs):
        if args[0] == "Get store":
            return True
        return False

    def text_input_side_effect(*args, **kwargs):
        return "store_name"

    with ExitStack() as stack:
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_error = stack.enter_context(patch("src.frontend.st.error"))
        mock_get = stack.enter_context(patch("src.frontend.requests.get"))
        mock_session_state = stack.enter_context(patch("src.frontend.st.session_state"))
        mock_text_input = stack.enter_context(patch("src.frontend.st.text_input"))

        mock_button.side_effect = button_side_effect
        mock_get.return_value.status_code = 400
        store_data = {"id": 1, "name": "store_name", "owner_id": 1}
        mock_get.return_value.json.return_value = store_data
        cookies = {"fastapiusersauth", "token"}
        mock_session_state.__getitem__.return_value = cookies
        mock_text_input.side_effect = text_input_side_effect

        main_page()

        mock_get.assert_called_once_with(
            f"{base_url}/store/store_name", cookies=cookies, timeout=TIMEOUT
        )
        mock_error.assert_called_once_with("Store not found")


def test_main_page_delete_store():
    def button_side_effect(*args, **kwargs):
        if args[0] == "Delete store":
            return True
        return False

    def text_input_side_effect(*args, **kwargs):
        return "store_name"

    with ExitStack() as stack:
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_success = stack.enter_context(patch("src.frontend.st.success"))
        mock_delete = stack.enter_context(patch("src.frontend.requests.delete"))
        mock_session_state = stack.enter_context(patch("src.frontend.st.session_state"))
        mock_text_input = stack.enter_context(patch("src.frontend.st.text_input"))

        mock_button.side_effect = button_side_effect
        mock_delete.return_value.status_code = 200
        cookies = {"fastapiusersauth", "token"}
        mock_session_state.__getitem__.return_value = cookies
        mock_text_input.side_effect = text_input_side_effect

        main_page()

        mock_delete.assert_called_once_with(
            f"{base_url}/store/store_name", cookies=cookies, timeout=TIMEOUT
        )
        mock_success.assert_called_once_with("Store deleted successfully!")


def test_main_page_delete_store_failure():
    def button_side_effect(*args, **kwargs):
        if args[0] == "Delete store":
            return True
        return False

    def text_input_side_effect(*args, **kwargs):
        return "store_name"

    with ExitStack() as stack:
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_error = stack.enter_context(patch("src.frontend.st.error"))
        mock_delete = stack.enter_context(patch("src.frontend.requests.delete"))
        mock_session_state = stack.enter_context(patch("src.frontend.st.session_state"))
        mock_text_input = stack.enter_context(patch("src.frontend.st.text_input"))

        mock_button.side_effect = button_side_effect
        mock_delete.return_value.status_code = 400
        cookies = {"fastapiusersauth", "token"}
        mock_session_state.__getitem__.return_value = cookies
        mock_text_input.side_effect = text_input_side_effect

        main_page()

        mock_delete.assert_called_once_with(
            f"{base_url}/store/store_name", cookies=cookies, timeout=TIMEOUT
        )
        mock_error.assert_called_once_with("Failed to delete store")


def test_main_page_add_package():
    def button_side_effect(*args, **kwargs):
        if args[0] == "Add package":
            return True
        return False

    def text_input_side_effect(*args, **kwargs):
        if args[0] == "Enter store name":
            return "store_name"

        return "package_name"

    with ExitStack() as stack:
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_success = stack.enter_context(patch("src.frontend.st.success"))
        mock_post = stack.enter_context(patch("src.frontend.requests.post"))
        mock_session_state = stack.enter_context(patch("src.frontend.st.session_state"))
        mock_text_input = stack.enter_context(patch("src.frontend.st.text_input"))

        mock_button.side_effect = button_side_effect
        mock_post.return_value.status_code = 200
        cookies = {"fastapiusersauth", "token"}
        mock_session_state.__getitem__.return_value = cookies
        mock_text_input.side_effect = text_input_side_effect

        main_page()

        mock_post.assert_called_once_with(
            f"{base_url}/store/store_name/package/package_name",
            cookies=cookies,
            timeout=None,
        )
        mock_success.assert_called_once_with("Package added successfully!")


def test_main_page_add_package_failure():
    def button_side_effect(*args, **kwargs):
        if args[0] == "Add package":
            return True
        return False

    def text_input_side_effect(*args, **kwargs):
        if args[0] == "Enter store name":
            return "store_name"

        return "package_name"

    with ExitStack() as stack:
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_error = stack.enter_context(patch("src.frontend.st.error"))
        mock_post = stack.enter_context(patch("src.frontend.requests.post"))
        mock_session_state = stack.enter_context(patch("src.frontend.st.session_state"))
        mock_text_input = stack.enter_context(patch("src.frontend.st.text_input"))

        mock_button.side_effect = button_side_effect
        mock_post.return_value.status_code = 400
        cookies = {"fastapiusersauth", "token"}
        mock_session_state.__getitem__.return_value = cookies
        mock_text_input.side_effect = text_input_side_effect

        main_page()

        mock_post.assert_called_once_with(
            f"{base_url}/store/store_name/package/package_name",
            cookies=cookies,
            timeout=None,
        )
        mock_error.assert_called_once_with("Failed to add package")


def test_main_page_add_package_warning():
    def button_side_effect(*args, **kwargs):
        if args[0] == "Add package":
            return True
        return False

    def text_input_side_effect(*args, **kwargs):
        return None

    with ExitStack() as stack:
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_warning = stack.enter_context(patch("src.frontend.st.warning"))
        mock_text_input = stack.enter_context(patch("src.frontend.st.text_input"))

        mock_button.side_effect = button_side_effect
        mock_text_input.side_effect = text_input_side_effect

        main_page()

        mock_warning.assert_called_once_with(
            "Please enter both store name and package name"
        )


def test_main_page_delete_package():
    def button_side_effect(*args, **kwargs):
        if args[0] == "Delete package":
            return True
        return False

    def text_input_side_effect(*args, **kwargs):
        if args[0] == "Enter store name":
            return "store_name"

        return "package_name"

    with ExitStack() as stack:
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_success = stack.enter_context(patch("src.frontend.st.success"))
        mock_delete = stack.enter_context(patch("src.frontend.requests.delete"))
        mock_session_state = stack.enter_context(patch("src.frontend.st.session_state"))
        mock_text_input = stack.enter_context(patch("src.frontend.st.text_input"))

        mock_button.side_effect = button_side_effect
        mock_delete.return_value.status_code = 200
        cookies = {"fastapiusersauth", "token"}
        mock_session_state.__getitem__.return_value = cookies
        mock_text_input.side_effect = text_input_side_effect

        main_page()

        mock_delete.assert_called_once_with(
            f"{base_url}/store/store_name/package/package_name",
            cookies=cookies,
            timeout=TIMEOUT,
        )
        mock_success.assert_called_once_with("Package deleted successfully!")


def test_main_page_delete_package_failure():
    def button_side_effect(*args, **kwargs):
        if args[0] == "Delete package":
            return True
        return False

    def text_input_side_effect(*args, **kwargs):
        if args[0] == "Enter store name":
            return "store_name"

        return "package_name"

    with ExitStack() as stack:
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_error = stack.enter_context(patch("src.frontend.st.error"))
        mock_delete = stack.enter_context(patch("src.frontend.requests.delete"))
        mock_session_state = stack.enter_context(patch("src.frontend.st.session_state"))
        mock_text_input = stack.enter_context(patch("src.frontend.st.text_input"))

        mock_button.side_effect = button_side_effect
        mock_delete.return_value.status_code = 400
        cookies = {"fastapiusersauth", "token"}
        mock_session_state.__getitem__.return_value = cookies
        mock_text_input.side_effect = text_input_side_effect

        main_page()

        mock_delete.assert_called_once_with(
            f"{base_url}/store/store_name/package/package_name",
            cookies=cookies,
            timeout=TIMEOUT,
        )
        mock_error.assert_called_once_with("Failed to delete package")


def test_main_page_get_package_meta():
    def button_side_effect(*args, **kwargs):
        if args[0] == "Get package meta":
            return True
        return False

    def text_input_side_effect(*args, **kwargs):
        if args[0] == "Enter store name":
            return "store_name"

        return "package_name"

    with ExitStack() as stack:
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_write = stack.enter_context(patch("src.frontend.st.write"))
        mock_get = stack.enter_context(patch("src.frontend.requests.get"))
        mock_session_state = stack.enter_context(patch("src.frontend.st.session_state"))
        mock_text_input = stack.enter_context(patch("src.frontend.st.text_input"))

        mock_button.side_effect = button_side_effect
        mock_get.return_value.status_code = 200
        package_meta = {"present": True, "closure_size": 1}
        mock_get.return_value.json.return_value = package_meta
        cookies = {"fastapiusersauth", "token"}
        mock_session_state.__getitem__.return_value = cookies
        mock_text_input.side_effect = text_input_side_effect

        main_page()

        mock_get.assert_called_once_with(
            f"{base_url}/store/store_name/package/package_name",
            cookies=cookies,
            timeout=TIMEOUT,
        )
        calls = [
            call("Package package_name in store store_name:"),
            call("Present: True"),
            call("Closure Size: 1"),
        ]
        mock_write.assert_has_calls(calls)


def test_main_page_get_package_meta_failure():
    def button_side_effect(*args, **kwargs):
        if args[0] == "Get package meta":
            return True
        return False

    def text_input_side_effect(*args, **kwargs):
        if args[0] == "Enter store name":
            return "store_name"

        return "package_name"

    with ExitStack() as stack:
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_error = stack.enter_context(patch("src.frontend.st.error"))
        mock_get = stack.enter_context(patch("src.frontend.requests.get"))
        mock_session_state = stack.enter_context(patch("src.frontend.st.session_state"))
        mock_text_input = stack.enter_context(patch("src.frontend.st.text_input"))

        mock_button.side_effect = button_side_effect
        mock_get.return_value.status_code = 400
        package_meta = {"present": True, "closure_size": 1}
        mock_get.return_value.json.return_value = package_meta
        cookies = {"fastapiusersauth", "token"}
        mock_session_state.__getitem__.return_value = cookies
        mock_text_input.side_effect = text_input_side_effect

        main_page()

        mock_get.assert_called_once_with(
            f"{base_url}/store/store_name/package/package_name",
            cookies=cookies,
            timeout=TIMEOUT,
        )
        mock_error.assert_called_once_with("Failed to get package meta")


def test_main_page_get_paths_difference():
    def button_side_effect(*args, **kwargs):
        if args[0] == "Get paths difference":
            return True
        return False

    def text_input_side_effect(*args, **kwargs):
        if args[0] == "Enter store name":
            return "store_name"

        return "other_store_name"

    with ExitStack() as stack:
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_write = stack.enter_context(patch("src.frontend.st.write"))
        mock_get = stack.enter_context(patch("src.frontend.requests.get"))
        mock_session_state = stack.enter_context(patch("src.frontend.st.session_state"))
        mock_text_input = stack.enter_context(patch("src.frontend.st.text_input"))

        mock_button.side_effect = button_side_effect
        mock_get.return_value.status_code = 200
        paths_difference = {
            "absent_in_store_1": ["path_1"],
            "absent_in_store_2": ["path_2", "path_3"],
        }
        mock_get.return_value.json.return_value = paths_difference
        cookies = {"fastapiusersauth", "token"}
        mock_session_state.__getitem__.return_value = cookies
        mock_text_input.side_effect = text_input_side_effect

        main_page()

        mock_get.assert_called_once_with(
            f"{base_url}/store/store_name/difference/other_store_name",
            cookies=cookies,
            timeout=TIMEOUT,
        )

        calls = [
            call("Paths absent in store 1:"),
            call("path_1"),
            call("Paths absent in store 2:"),
            call("path_2"),
            call("path_3"),
        ]
        mock_write.assert_has_calls(calls)


def test_main_page_get_paths_difference_failure():
    def button_side_effect(*args, **kwargs):
        if args[0] == "Get paths difference":
            return True
        return False

    def text_input_side_effect(*args, **kwargs):
        if args[0] == "Enter store name":
            return "store_name"

        return "other_store_name"

    with ExitStack() as stack:
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_error = stack.enter_context(patch("src.frontend.st.error"))
        mock_get = stack.enter_context(patch("src.frontend.requests.get"))
        mock_session_state = stack.enter_context(patch("src.frontend.st.session_state"))
        mock_text_input = stack.enter_context(patch("src.frontend.st.text_input"))

        mock_button.side_effect = button_side_effect
        mock_get.return_value.status_code = 400
        paths_difference = {
            "absent_in_store_1": ["path_1"],
            "absent_in_store_2": ["path_2", "path_3"],
        }
        mock_get.return_value.json.return_value = paths_difference
        cookies = {"fastapiusersauth", "token"}
        mock_session_state.__getitem__.return_value = cookies
        mock_text_input.side_effect = text_input_side_effect

        main_page()

        mock_get.assert_called_once_with(
            f"{base_url}/store/store_name/difference/other_store_name",
            cookies=cookies,
            timeout=TIMEOUT,
        )
        mock_error.assert_called_once_with("Failed to get paths difference")


def test_main_page_get_closures_difference():
    def button_side_effect(*args, **kwargs):
        if args[0] == "Get closures difference":
            return True
        return False

    def text_input_side_effect(*args, **kwargs):
        if args[0] == "Enter store name":
            return "store_name"

        if args[0] == "Enter other store name":
            return "other_store_name"

        if args[0] == "Enter package name":
            return "package_name"

        if args[0] == "Enter other package name":
            return "other_package_name"

        return ""

    with ExitStack() as stack:
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_write = stack.enter_context(patch("src.frontend.st.write"))
        mock_get = stack.enter_context(patch("src.frontend.requests.get"))
        mock_session_state = stack.enter_context(patch("src.frontend.st.session_state"))
        mock_text_input = stack.enter_context(patch("src.frontend.st.text_input"))

        mock_button.side_effect = button_side_effect
        mock_get.return_value.status_code = 200
        closures_difference = {
            "difference": [
                {
                    "package_name": "name_1",
                    "version_update": {"old": "1.0.0", "new": "2.0.0"},
                    "size_update": 10,
                },
                {
                    "package_name": "name_2",
                    "version_update": {"old": "1.0.0", "new": "2.0.0"},
                    "size_update": 10,
                },
            ]
        }
        mock_get.return_value.json.return_value = closures_difference
        cookies = {"fastapiusersauth", "token"}
        mock_session_state.__getitem__.return_value = cookies
        mock_text_input.side_effect = text_input_side_effect

        main_page()

        mock_get.assert_called_once_with(
            f"{base_url}/store/store_name/package/package_name/closure-difference/other_store_name/other_package_name",
            cookies=cookies,
            timeout=TIMEOUT,
        )

        calls = [
            call("Closure difference:"),
            call("Package name: name_1"),
            call("Version update: 1.0.0 -> 2.0.0"),
            call("Size update: 10"),
            call("---"),
            call("Package name: name_2"),
            call("Version update: 1.0.0 -> 2.0.0"),
            call("Size update: 10"),
            call("---"),
        ]

        assert mock_write.call_args_list == calls


def test_main_page_get_closures_difference_failure():
    def button_side_effect(*args, **kwargs):
        if args[0] == "Get closures difference":
            return True
        return False

    def text_input_side_effect(*args, **kwargs):
        if args[0] == "Enter store name":
            return "store_name"

        if args[0] == "Enter other store name":
            return "other_store_name"

        if args[0] == "Enter package name":
            return "package_name"

        if args[0] == "Enter other package name":
            return "other_package_name"

        return ""

    with ExitStack() as stack:
        mock_button = stack.enter_context(patch("src.frontend.st.button"))
        mock_error = stack.enter_context(patch("src.frontend.st.error"))
        mock_get = stack.enter_context(patch("src.frontend.requests.get"))
        mock_session_state = stack.enter_context(patch("src.frontend.st.session_state"))
        mock_text_input = stack.enter_context(patch("src.frontend.st.text_input"))

        mock_button.side_effect = button_side_effect
        mock_get.return_value.status_code = 400
        closures_difference = {
            "difference": [
                {
                    "package_name": "name_1",
                    "version_update": {"old": "1.0.0", "new": "2.0.0"},
                    "size_update": 10,
                },
                {
                    "package_name": "name_2",
                    "version_update": {"old": "1.0.0", "new": "2.0.0"},
                    "size_update": 10,
                },
            ]
        }
        mock_get.return_value.json.return_value = closures_difference
        cookies = {"fastapiusersauth", "token"}
        mock_session_state.__getitem__.return_value = cookies
        mock_text_input.side_effect = text_input_side_effect

        main_page()

        mock_get.assert_called_once_with(
            f"{base_url}/store/store_name/package/package_name/closure-difference/other_store_name/other_package_name",
            cookies=cookies,
            timeout=TIMEOUT,
        )
        mock_error.assert_called_once_with("Failed to get closures difference")
