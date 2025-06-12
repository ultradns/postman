#!/usr/bin/env python3

import json
import os
import sys
import requests
from pathlib import Path
from typing import Dict, List, Set
from jsonschema import validate

# Properties to remove from Postman files
METADATA_PROPERTIES = {
    '_postman_id',
    '_exporter_id',
    'id',
    'uid',
    'owner',
    'createdAt',
    'updatedAt',
    'lastUpdatedBy',
    'lastRevision',
}

# Required schema versions for Postman files
COLLECTION_SCHEMA = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"

# Fixed names for collection and environment
COLLECTION_NAME = "API Documentation"
ENVIRONMENT_NAME = "Sample Environment"

def fetch_schema(url: str) -> dict:
    """Fetch a JSON schema from a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Warning: Could not fetch schema from {url}: {str(e)}", file=sys.stderr)
        return None

def validate_environment(data: dict) -> bool:
    """Validate a Postman environment file has the required fields."""
    if not isinstance(data, dict):
        print("Error: Environment file must be a JSON object", file=sys.stderr)
        return False
    
    if 'name' not in data:
        print("Error: Environment file must have a 'name' field", file=sys.stderr)
        return False
    
    if 'values' not in data:
        print("Error: Environment file must have a 'values' field", file=sys.stderr)
        return False
    
    if not isinstance(data['values'], list):
        print("Error: Environment 'values' field must be an array", file=sys.stderr)
        return False
    
    return True

def remove_metadata(data: Dict, properties: Set[str]) -> Dict:
    """Recursively remove specified properties from a dictionary."""
    if not isinstance(data, dict):
        return data

    result = {}
    for key, value in data.items():
        if key in properties:
            continue
        
        if isinstance(value, dict):
            result[key] = remove_metadata(value, properties)
        elif isinstance(value, list):
            result[key] = [remove_metadata(item, properties) if isinstance(item, dict) else item for item in value]
        else:
            result[key] = value
    
    return result

def sanitize_file(file_path: Path) -> bool:
    """Sanitize a single Postman file and return True if changes were made."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate the file before sanitizing
        if file_path.name.endswith('.postman_collection.json'):
            schema = fetch_schema(COLLECTION_SCHEMA)
            if schema:
                validate(instance=data, schema=schema)
            # Set fixed collection name
            if 'info' in data and 'name' in data['info']:
                data['info']['name'] = COLLECTION_NAME
        elif file_path.name.endswith('.postman_environment.json'):
            if not validate_environment(data):
                return False
            # Set fixed environment name
            if 'name' in data:
                data['name'] = ENVIRONMENT_NAME
        else:
            print(f"Unknown file type: {file_path}", file=sys.stderr)
            return False
        
        # Preserve the original schema
        original_schema = data.get('info', {}).get('schema') if 'info' in data else data.get('schema')
        
        # Remove metadata
        sanitized_data = remove_metadata(data, METADATA_PROPERTIES)
        
        # Restore schema if it was present
        if original_schema:
            if 'info' in sanitized_data:
                sanitized_data['info']['schema'] = original_schema
            else:
                sanitized_data['schema'] = original_schema
        
        # Format the JSON with consistent indentation
        new_data = json.dumps(sanitized_data, indent=2)
        
        # Compare the sanitized data with original
        original_data = json.dumps(data, indent=2)
        if original_data != new_data:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_data)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}", file=sys.stderr)
        return False

def find_postman_files(directory: Path) -> List[Path]:
    """Find all Postman collection and environment files in the directory."""
    patterns = ['*.postman_collection.json', '*.postman_environment.json']
    files = []
    for pattern in patterns:
        files.extend(directory.rglob(pattern))
    return files

def main():
    if len(sys.argv) != 2:
        print("Usage: python sanitize_postman.py <directory>")
        sys.exit(1)
    
    directory = Path(sys.argv[1])
    if not directory.exists():
        print(f"Directory {directory} does not exist", file=sys.stderr)
        sys.exit(1)
    
    files = find_postman_files(directory)
    if not files:
        print("No Postman files found to sanitize")
        sys.exit(0)
    
    modified_files = []
    for file_path in files:
        if sanitize_file(file_path):
            modified_files.append(str(file_path))
    
    if modified_files:
        print("Modified files:")
        for file in modified_files:
            print(f"- {file}")
    else:
        print("No files were modified")
    
    sys.exit(0)

if __name__ == '__main__':
    main() 