# pyright: reportAttributeAccessIssue = false

import streamlit as st
import requests

base_url = "http://localhost:8000"
st.title("Nix store management system")

st.header("Create store")
store_name_input_key = "create_store_name_input"
store_name = st.text_input("Store name", key=store_name_input_key)
if st.button("Create store"):
    response = requests.post(f"{base_url}/store", json={"name": store_name})
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


def get_store_id(store_name):
    response = requests.get(f"{base_url}/store/{store_name}")
    if response.status_code == 200:
        store_data = response.json()
        return store_data['id']
    return None


st.header("Add package")
store_name = st.text_input(
    "Enter store name", key="add_package_store_name_input")
package_name = st.text_input("Package name", key="package_name_input")
if st.button("Add package"):
    if store_name and package_name:
        store_id = get_store_id(store_name)
        if store_id:
            payload = {"name": package_name, "store_id": store_id}
            response = requests.post(
                f"{base_url}/store/{store_name}/package", json=payload)
            if response.status_code == 200:
                st.success("Package added successfully!")
            else:
                st.error("Failed to add package")
        else:
            st.error("Store not found")
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
