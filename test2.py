import requests
import json


def testQuery(username, query): 
    test_payload = {
        "username": username,
        "query": query
    }

    response = requests.post(
        "http://localhost:3000/query",
        json=test_payload,
        headers={"Content-Type": "application/json"}
    )

    print(response.status_code)
    print(response.json())
    return response.json().get("response")

if __name__ == "__main__":
    testQuery("test_user", "What services does Acme Corporation offer?")
