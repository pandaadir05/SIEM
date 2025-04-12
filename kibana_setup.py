import requests
import os

KIBANA_URL = os.environ.get("KIBANA_URL", "http://localhost:5601")
INDEX_PATTERN_NAME = "logs"
TIME_FIELD_NAME = "@timestamp"

def create_index_pattern():
    # Kibana Saved Objects API
    api_endpoint = f"{KIBANA_URL}/api/saved_objects/index-pattern/{INDEX_PATTERN_NAME}"

    headers = {
        "kbn-xsrf": "true",  # Required by Kibana API
        "Content-Type": "application/json"
    }

    payload = {
        "attributes": {
            "title": INDEX_PATTERN_NAME,
            "timeFieldName": TIME_FIELD_NAME
        }
    }

    resp = requests.post(api_endpoint, headers=headers, json=payload)
    if resp.status_code in [200, 201]:
        print(f"Index pattern '{INDEX_PATTERN_NAME}' created/updated successfully in Kibana.")
    else:
        print(f"Failed to create index pattern. Status: {resp.status_code}, Response: {resp.text}")

if __name__ == "__main__":
    create_index_pattern()
