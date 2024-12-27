# Test the API connection
import requests

test_payload = {
    "username": "test_user",
    "query": "What services does Acme Corporation offer?"
}

response = requests.post(
    "http://localhost:3000/query",
    json=test_payload,
    headers={"Content-Type": "application/json"}
)

print(response.status_code)
print(response.json())