import pytest
from unittest.mock import patch
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

@pytest.fixture(scope="module")
def driver():
    webdriver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=webdriver_service, executable_path='/usr/bin/google-chrome')
    yield driver
    driver.quit()

def test_register(driver):
    driver.get("http://localhost:8501")

    register_button = driver.find_element(By.XPATH, "//label[contains(text(), 'Register')]")
    register_button.click()

    with patch("src.frontend.requests.post") as mock_post:
        with patch("src.frontend.st.success") as mock_success:
            mock_post.return_value.status_code = 201
            mock_post.return_value.json.return_value = {"message": "User created"}

            email_input = driver.find_element(By.NAME, "Email")
            email_input.send_keys("user@example.com")

            password_input = driver.find_element(By.NAME, "Password")
            password_input.send_keys("testpassword")

            register_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Register')]")
            register_button.click()

            assert mock_post.called
            assert mock_success.called
