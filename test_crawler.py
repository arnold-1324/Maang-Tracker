
import requests
import json

url = "http://localhost:5100/api/jobs/crawl"
payload = {
    "url": "https://www.amazon.jobs/en/jobs/2841682/software-development-engineer-amazon-pay",
    "save": True
}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
