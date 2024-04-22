# pyright: reportAttributeAccessIssue = false
# pylint: disable=no-member

import streamlit as st
import requests
import extra_streamlit_components as stx

base_url = "http://localhost:8000"

@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

def main_page():
    st.title("Nix store management system")
    st.header("Create store")
    store_name_input_key = "create_store_name_input"
    store_name = st.text_input("Store name", key=store_name_input_key)
    if st.button("Create store"):
        response = requests.post(f"{base_url}/store/{store_name}")
        if response.status_code == 200:
            st.success("Store created successfully!")
        else:
            st.error("Failed to create store")

    st.header("Get store")
    get_store_name_input_key = "get_store_name_input"
    store_name = st.text_input("Enter store name", key=get_store_name_input_key)
    if st.button("Get store"):
        response = requests.get(f"{base_url}/store/{store_name}")
        if response.status_code == 200:
            store_data = response.json()
            st.write(f"Store ID: {store_data['id']}")
            st.write(f"Store name: {store_data['name']}")
            st.write(f"Owner ID: {store_data['owner_id']}")
        else:
            st.error("Store not found")

    st.header("Delete store")
    delete_store_name_input_key = "delete_store_name_input"
    store_name = st.text_input("Enter store name", key=delete_store_name_input_key)
    if st.button("Delete store"):
        response = requests.delete(f"{base_url}/store/{store_name}")
        if response.status_code == 200:
            st.success("Store deleted successfully!")
        else:
            st.error("Failed to delete store")

    st.header("Add package")
    store_name = st.text_input(
        "Enter store name", key="add_package_store_name_input")
    package_name = st.text_input("Package name", key="package_name_input")
    if st.button("Add package"):
        if store_name and package_name:
            response = requests.post(
                    f"{base_url}/store/{store_name}/package/{package_name}")
            if response.status_code == 200:
                st.success("Package added successfully!")
            else:
                st.error("Failed to add package")
        else:
            st.warning("Please enter both store name and package name")


    st.header("Delete package")
    delete_package_store_name_input_key = "delete_package_store_name_input"
    store_name = st.text_input("Enter store name",
                            key=delete_package_store_name_input_key)
    delete_package_name_input_key = "delete_package_name_input"
    package_name = st.text_input("Package name", key=delete_package_name_input_key)
    if st.button("Delete package"):
        response = requests.delete(
            f"{base_url}/store/{store_name}/package/{package_name}")
        if response.status_code == 200:
            st.success("Package deleted successfully!")
        else:
            st.error("Failed to delete package")

    st.header("Get package meta")
    store_name = st.text_input("Enter store name", key="get_package_meta_store_name_input")
    package_name = st.text_input("Enter package name", key="get_package_meta_package_name_input")
    if st.button("Get package meta"):
        if store_name and package_name:
            response = requests.get(f"{base_url}/store/{store_name}/package/{package_name}")
            if response.status_code == 200:
                package_meta = response.json()
                st.write(f"Package {package_name} in store {store_name}:")
                st.write(f"Present: {package_meta['present']}")
                st.write(f"Closure Size: {package_meta['closure_size']}")
            else:
                st.error("Failed to get package meta")
        else:
            st.warning("Please enter both store name and package name")

    st.header("Get paths difference")
    store_name = st.text_input(
        "Enter store name", key="get_paths_store_name_input")
    other_store_name = st.text_input(
        "Enter other store name", key="get_paths_other_store_name_input")
    if st.button("Get paths difference"):
        if store_name and other_store_name:
            response = requests.get(
                f"{base_url}/store/{store_name}/difference/{other_store_name}")
            if response.status_code == 200:
                paths_difference = response.json()
                st.write("Paths absent in store 1:")
                for path in paths_difference["absent_in_store_1"]:
                    st.write(path)
                st.write("Paths absent in store 2:")
                for path in paths_difference["absent_in_store_2"]:
                    st.write(path)
            else:
                st.error("Failed to get paths difference")
        else:
            st.warning("Please enter both store names")

    st.header("Get closures difference")
    store_name = st.text_input(
        "Enter store name", key="get_closures_store_name_input")
    package_name = st.text_input(
        "Enter package name", key="get_closures_package_name_input")
    other_store_name = st.text_input(
        "Enter other store name", key="get_closures_other_store_name_input")
    other_package_name = st.text_input(
        "Enter other package name", key="get_closures_other_package_name_input")
    if st.button("Get closures difference"):
        if store_name and package_name and other_store_name and other_package_name:
            response = requests.get(
                f"{base_url}/store/{store_name}/package/{package_name}/closure-difference/{other_store_name}/{other_package_name}")
            if response.status_code == 200:
                closures_difference = response.json()
                st.write("Closure difference:")
                for change in closures_difference["difference"]:
                    st.write(f"Package name: {change['package_name']}")
                    st.write(f"Version update: {change['version_update']['old']} -> {change['version_update']['new']}")
                    st.write(f"Size update: {change['size_update']}")
                    st.write("---")
            else:
                st.error("Failed to get closures difference")
        else:
            st.warning("Please enter all store and package names")


def login_page():
    st.title("Login")

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_button"):
        response = requests.post(
            f"{base_url}/auth/jwt/login",
            data={"username": email, "password": password},
        )
        if response.status_code == 204:
            cookies = response.headers.get("set-cookie")
            print(cookies)
            st.session_state["Set_cookies"] = cookies
            st.success("Login successful")
            st.session_state.is_authorized = True
            st.experimental_rerun()
        else:
            st.error("Login failed. Please check your credentials.")


def register_page():
    st.title("Register")

    email = st.text_input("Email", key="register_email")
    password = st.text_input("Password", type="password", key="register_password")

    if st.button("Register", key="register_button"):
        payload = {
            "email": email,
            "password": password,
            "is_active": True,
            "is_superuser": False,
            "is_verified": False
        }
        response = requests.post(
            f"{base_url}/auth/register",
            json=payload,
        )
        if response.status_code == 201:
            st.success("Registration successful")
        else:
            st.error("Registration failed")


def logout():
    st.title("Logout")
    if st.button("Logout"):
        response = requests.post(
            f"{base_url}/auth/jwt/logout",
        )
        if response.status_code == 204:
            st.success("Logout successful")
            st.session_state.is_authorized = False
            st.experimental_rerun()
        else:
            st.error("Logout failed")


def main():
    
    if "Set_cookies" in st.session_state:
        print(st.session_state["Set_cookies"])
        cookie_manager.set('set-cookie', st.session_state["Set_cookies"])
        
    st.sidebar.title("Navigation")
    if "is_authorized" not in st.session_state:
        st.session_state["is_authorized"] = False

    if st.session_state.is_authorized:
        page = st.sidebar.radio("Go to", ["Main Page", "Logout"])
    else:
        page = st.sidebar.radio("Go to", ["Login", "Register"])

    if page == "Login":
        login_page()
    elif page == "Register":
        register_page()
    elif page == "Main Page":
        if st.session_state.is_authorized:
            main_page()
        else:
            st.warning("You are not authorized to view this page. Please login first.")
    elif page == "Logout":
        if st.session_state.is_authorized:
            logout()
        else:
            st.warning("You are not authorized. Please login first")


if __name__ == "__main__":
    main()
