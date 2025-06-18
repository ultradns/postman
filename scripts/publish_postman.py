#!/usr/bin/env python3

import json
import os
import sys
import requests
from pathlib import Path

POSTMAN_API_BASE = "https://api.getpostman.com"

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file {file_path}: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        sys.exit(1)

def publish_to_postman(file_path, workspace_id, api_key, is_collection=True):
    """Publish a collection or environment to Postman."""
    data = load_json_file(file_path)
    
    # Prepare the request payload
    payload = {
        "workspace": workspace_id
    }
    
    if is_collection:
        endpoint = f"{POSTMAN_API_BASE}/collections"
        payload["collection"] = data
    else:
        endpoint = f"{POSTMAN_API_BASE}/environments"
        payload["environment"] = data

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        print(f"Successfully published {'collection' if is_collection else 'environment'}: {file_path}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error publishing to Postman: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        sys.exit(1)

def main():
    # Check for required environment variables
    api_key = os.getenv('POSTMAN_API_KEY')
    workspace_id = os.getenv('POSTMAN_WORKSPACE_ID')
    
    if not api_key or not workspace_id:
        print("Error: POSTMAN_API_KEY and POSTMAN_WORKSPACE_ID environment variables must be set")
        sys.exit(1)

    # Get the directory containing the Postman files
    if len(sys.argv) != 2:
        print("Usage: python publish_postman.py <directory>")
        sys.exit(1)

    directory = Path(sys.argv[1])
    if not directory.exists():
        print(f"Directory not found: {directory}")
        sys.exit(1)

    # Find and publish all collection and environment files
    for file_path in directory.glob('*.postman_collection.json'):
        publish_to_postman(file_path, workspace_id, api_key, is_collection=True)

    for file_path in directory.glob('*.postman_environment.json'):
        publish_to_postman(file_path, workspace_id, api_key, is_collection=False)

if __name__ == "__main__":
    main() 