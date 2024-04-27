from unittest.mock import patch

from src.frontend import TIMEOUT, base_url, register_page


def test_register_page_success():
    with patch("src.frontend.requests.post") as mock_post:
        with patch("src.frontend.st.button") as mock_button:
            with patch("src.frontend.st.text_input") as mock_text_input:
                with patch("src.frontend.st.success") as mock_success:
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
    with patch("src.frontend.requests.post") as mock_post:
        with patch("src.frontend.st.button") as mock_button:
            with patch("src.frontend.st.text_input") as mock_text_input:
                with patch("src.frontend.st.error") as mock_error:
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


# def test_login_page_success():
#     with patch("src.frontend.requests.post") as mock_post:
#         with patch("src.frontend.st.button") as mock_button:
#             with patch("src.frontend.st.text_input") as mock_text_input:
#                 with patch("src.frontend.st.success") as mock_success:
#                     mock_post.return_value.status_code = 200
#                     mock_post.return_value.json.return_value = {"status": "success"}

#                     mock_button.return_value = True
#                     mock_text_input.side_effect = ["
