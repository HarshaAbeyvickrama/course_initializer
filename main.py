import json
import os

import pandas as pd

import requests

url = "https://nebula-framework-esmukdjmcq-as.a.run.app"
access_token = None
course_id = '3d8949fa-6f4c-49c3-9d8f-1cfa89880a9c'
email = "2019is033@stu.ucsc.cmb.ac.lk"


def authenticate_with_oauth2_token(username, password):
    global access_token
    token_url = f"{url}/token"
    data = {
        "grant_type": "password",
        "username": username,
        "password": password,
    }

    response = requests.post(token_url, data=data)

    if response.status_code == 200:
        # Authentication successful
        access_token = response.json()["access_token"]
        print("Authentication successful. Access Token:", access_token)
    else:
        # Authentication failed
        raise Exception(f"Authentication failed: {response.status_code} - {response.text}")


def create_bucket(bucket_data):
    global url, access_token
    buckets_url = f"{url}/buckets/"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.post(buckets_url, headers=headers, json=bucket_data)

    if response.status_code == 201:
        # Request successful
        return response.json()
    else:
        # Request failed
        raise Exception(f"Failed to create bucket: {response.status_code} - {response.text}")


def save_to_excel(file_name, bucket_id, quiz_id):
    excel_file = "bucket_data.xlsx"

    # Check if the Excel file already exists
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file)
    else:
        df = pd.DataFrame(columns=["File Name", "bucket_id", "quiz_id"])

    # Append new data to the DataFrame
    new_data = pd.DataFrame({"File Name": [file_name], "bucket_id": [bucket_id], "quiz_id": [quiz_id]})
    df = pd.concat([df, new_data], ignore_index=True)

    # Save to Excel
    df.to_excel(excel_file, index=False)


def create_quiz(bucket_id, duration, filename, course_id):
    global url, access_token, email
    quizzes_url = f"{url}/quizzes/"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }

    data = {
        "title": filename,
        "description": filename,
        "quiz_duration": duration,
        "due_date": "2024-02-10T17:43:52.779Z",
        "multiple_submissions": False,
        "late_submissions": False,
        "latest_submission": "2024-01-29T17:43:52.779Z",
        "bucket_id": bucket_id,
        "course": course_id,
        "open_date": "2024-02-01T17:43:52.779Z",
        "created_by": email
    }
    response = requests.post(quizzes_url, headers=headers, json=data)

    if response.status_code == 201:
        # Request successful
        return response.json()
    else:
        # Request failed
        raise Exception(f"Failed to create quiz: {response.status_code} - {response.text}")


def remove_json_extension(file_name):
    if file_name.endswith(".json"):
        return file_name[:-5]  # Remove the last 5 characters (".json")
    else:
        return file_name


def main():
    global access_token, course_id
    # Replace these values with your actual FastAPI application's URL, username, and password
    username = "team_nebula"
    password = "newyear@321xDaluben"

    try:
        authenticate_with_oauth2_token(username, password)

        # Path to the folder containing JSON files
        folder_path = "g_buckets"

        # Iterate through each file in the folder
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                file_path = os.path.join(folder_path, filename)

                # Read the JSON data from the file
                with open(file_path, "r") as file:
                    bucket_data = json.load(file)

                # Create the bucket using the copied data from the file
                duration = bucket_data['quiz_count'] * 2
                quiz_title = f'{bucket_data['title']} (quiz)'
                created_bucket = create_bucket(bucket_data)

                # Extract _id from the response
                bucket_id = created_bucket.get("_id", "")

                # Save to Excel

                print(f"Created Bucket from {filename}:", created_bucket)
                created_quiz = create_quiz(bucket_id, duration, quiz_title, course_id)
                print(f"Created quiz from {filename}:", created_quiz)
                quiz_id = created_quiz.get("_id", "")
                save_to_excel(bucket_data['title'], bucket_id, quiz_id)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
