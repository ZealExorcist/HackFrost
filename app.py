import streamlit as st
import requests
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import json

load_dotenv()
# MongoDB connection setup
client = MongoClient(os.getenv("MONGO_CLIENT"))  # replace with your MongoDB connection string
db = client["auth_app"]  # Create a database called auth_app
users_collection = db["users"]  # Create a collection called users

if "page" not in st.session_state:
    st.session_state.page = "form"  

def switch_page():
    st.session_state.page = "uploader"

if "name" not in st.session_state:
    st.session_state.name = None

if "email" not in st.session_state:
    st.session_state.email = None

if "file" not in st.session_state:
    st.session_state.file = None

if "region" not in st.session_state:
    st.session_state.region = None

@st.dialog("DELETE FILE: This action cannot be undone")
def delete_file():
    files = ["Select a file"]
    data = refresh()
    for file in data:
        files.append(file["fileName"])
    file = st.selectbox("Select a file to delete", files)
    if st.button("Delete"):
        uri = f"http://localhost:8080/api/v1/namespaces/final.code/files?path={file}"
        response = requests.delete(uri)
        if response.status_code == 200:
            st.success("File deleted successfully!")
        else:
            st.error("Failed to delete file.")
        st.stop()

def refresh():
    uri = "http://localhost:8080/api/v1/namespaces/final.code/files/directory"
    headers = {
    "Content-Type": "application/json",  # Adjust the content type if necessary
    }
    response = requests.get(uri, headers=headers)
    data = response.json()
    return data

def generate():
    files = ["Select a file"]
    data = refresh()
    for file in data:
        files.append(file["fileName"])
    url = "localhost:8080/api/v1/executions/final.code/final"
    payload = {'values': '["test.py"]'}
    response = requests.request("POST", url, data=payload, files=files)
    if response.status_code == 200:
        st.success("Report generated successfully! check the email")

def upload(file):
    
    uri = f"http://localhost:8080/api/v1/namespaces/final.code/files?path={file.name}"
    files = {
        "fileContent": (file.name, file, "application/octet-stream")
    }
    response = requests.post(uri, files=files)
    if response.status_code == 200:
        st.success("File uploaded successfully!")
    else:
        st.error("Failed to upload file.")

def save_email(email):
    uri = "http://localhost:8080/api/v1/namespaces/final.code/kv/email"
    payload = json.dumps(email)
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("PUT", uri, headers=headers, data=payload)

def save_region(region):
    uri = "http://localhost:8080/api/v1/namespaces/final.code/kv/region"
    payload = json.dumps(region)
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("PUT", uri, headers=headers, data=payload)


if st.session_state.page == "form": #dont mess with this 
    
    st.title("Preference Form")
    with st.form("preference_form"):
        name = st.text_input("Enter your Name", placeholder="Full Name")
        email = st.text_input("Enter your Email", placeholder="example@example.com")
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            if not name or not email:
                st.error("Please provide both your name and email.")
            else:
                st.session_state.name = name
                st.session_state.email = email
                save_email(email)
                switch_page()


elif st.session_state.page == "uploader":
    st.title("File Uploader")
    if "name" in st.session_state and "email" in st.session_state:
        st.write(f"**Welcome, {st.session_state.name}!**")
        st.write(f"**Email:** {st.session_state.email}")

    uploaded_file = st.file_uploader("Upload a file", type=["txt", "py", "java", "docx", "pdf"])
    with st.container():
        if st.button("Upload File"):
            upload(uploaded_file)
        if st.button("Delete File"):
            delete_file()

        if st.button("refresh"):
            data = refresh()
            for i in range(len(data)):
                st.write(data[i])
    
    region = st.text_input("Enter your Region")
    st.session_state.region = region
        
    if st.button("Get Report") and st.session_state.region is not None and st.session_state.email is not None:
        save_region(region)
        generate()