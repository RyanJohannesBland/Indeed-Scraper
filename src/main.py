import requests
import boto3
import random
from botocore.exceptions import ClientError


def get_configuration_set():
    ssm = boto3.client('ssm')
    api_key = ssm.get_parameter(Name='/indeed-scraper/api_key', WithDecryption=True)['Parameter']['Value']
    sender_email_address = ssm.get_parameter(Name='/indeed-scraper/sender_email', WithDecryption=True)['Parameter']['Value']
    receiver_email_address = ssm.get_parameter(Name='/indeed-scraper/receiver_email', WithDecryption=True)['Parameter']['Value']
    return api_key, sender_email_address, receiver_email_address


api_key, sender_email_address, receiver_email_address = get_configuration_set()


def has_keywords(text):
    keywords = [
        "python",
        "django",
        "flask",
        "fastapi",
        "node.js",
        "nodejs",
        "node",
        "react",
        "react.js",
        "reactjs",
        "aws",
    ]
    text = text.lower()
    return any(k in text for k in keywords)


def list_relevant_jobs(keyword, location):
    url = "https://api.hasdata.com/scrape/indeed/listing"
    params = {
        "keyword": keyword,
        "location": location,
        "start": random.randint(0, 250)  # Random start for pagination
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        filtered_jobs = []
        data = response.json()

        for job in data.get("jobs", []):
            title = job.get("title", "").lower()
            description = job.get("description", "").lower()
            url = job.get("url", "")
            date = job.get("isoDate", "")
            if has_keywords(title) or has_keywords(description):
                filtered_jobs.append({"title": title, "description": description, "url": url, "date": date})

        return filtered_jobs
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")
        return []


def email_jobs(jobs):
    ses_client = boto3.client("ses", region_name="us-east-1")
    subject = "Interesting Job Listings"
    body_text = "Here are Indeed job listings that match your parameters:\n\n"
    for job in jobs:
        body_text += f"{job['title']} - {job['url']} ({job['date']})\n"

    try:
        response = ses_client.send_email(
            Source=sender_email_address,
            Destination={"ToAddresses": [receiver_email_address]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body_text}}
            }
        )
        print(f"Email sent! Message ID: {response['MessageId']}")
    except ClientError as e:
        print(f"Failed to send email: {e.response['Error']['Message']}")


def handler(event, context):
    jobs = list_relevant_jobs("Software Engineer", "Remote")
    if jobs:
        email_jobs(jobs)
    else:
        print("No relevant jobs found.")
