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

def validate_collection_structure(data: dict) -> bool:
    """Validate Postman collection structure without relying on the broken schema."""
    # Check required top-level fields
    if 'info' not in data:
        print("Error: Collection missing 'info' field", file=sys.stderr)
        return False
    
    if 'item' not in data:
        print("Error: Collection missing 'item' field", file=sys.stderr)
        return False
    
    if not isinstance(data['item'], list):
        print("Error: Collection 'item' field must be an array", file=sys.stderr)
        return False
    
    # Validate info structure
    info = data['info']
    if not isinstance(info, dict):
        print("Error: Collection 'info' field must be an object", file=sys.stderr)
        return False
    
    if 'name' not in info:
        print("Error: Collection info missing 'name' field", file=sys.stderr)
        return False
    
    # Validate items recursively
    for i, item in enumerate(data['item']):
        if not validate_item_structure(item, f"item[{i}]"):
            return False
    
    return True

def validate_item_structure(item: dict, path: str) -> bool:
    """Validate individual item structure."""
    if not isinstance(item, dict):
        print(f"Error: {path} must be an object", file=sys.stderr)
        return False
    
    if 'name' not in item:
        print(f"Error: {path} missing 'name' field", file=sys.stderr)
        return False
    
    # Check if this is a folder (item-group) or a request (item)
    if 'item' in item:
        # This is a folder - validate nested items
        if not isinstance(item['item'], list):
            print(f"Error: {path}.item must be an array", file=sys.stderr)
            return False
        
        for j, nested_item in enumerate(item['item']):
            if not validate_item_structure(nested_item, f"{path}.item[{j}]"):
                return False
    elif 'request' in item:
        # This is a request - validate request structure
        if not validate_request_structure(item['request'], f"{path}.request"):
            return False
        
        # Validate response if present
        if 'response' in item:
            if not isinstance(item['response'], list):
                print(f"Error: {path}.response must be an array", file=sys.stderr)
                return False
            
            for j, response in enumerate(item['response']):
                if not validate_response_structure(response, f"{path}.response[{j}]"):
                    return False
    else:
        print(f"Error: {path} must have either 'item' (folder) or 'request' (request) field", file=sys.stderr)
        return False
    
    return True

def validate_request_structure(request: dict, path: str) -> bool:
    """Validate request structure."""
    if not isinstance(request, dict):
        print(f"Error: {path} must be an object", file=sys.stderr)
        return False
    
    # Check for required fields
    if 'method' not in request:
        print(f"Error: {path} missing 'method' field", file=sys.stderr)
        return False
    
    if 'url' not in request:
        print(f"Error: {path} missing 'url' field", file=sys.stderr)
        return False
    
    # Validate URL structure
    url = request['url']
    if isinstance(url, dict):
        if 'raw' not in url:
            print(f"Error: {path}.url missing 'raw' field", file=sys.stderr)
            return False
    
    return True

def validate_response_structure(response: dict, path: str) -> bool:
    """Validate response structure."""
    if not isinstance(response, dict):
        print(f"Error: {path} must be an object", file=sys.stderr)
        return False
    
    # Check for required fields
    if 'name' not in response:
        print(f"Error: {path} missing 'name' field", file=sys.stderr)
        return False
    
    if 'status' not in response:
        print(f"Error: {path} missing 'status' field", file=sys.stderr)
        return False
    
    if 'code' not in response:
        print(f"Error: {path} missing 'code' field", file=sys.stderr)
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

def fix_preview_language(data: Dict) -> Dict:
    """Fix _postman_previewlanguage fields that have empty string values."""
    if not isinstance(data, dict):
        return data

    result = {}
    for key, value in data.items():
        if key == '_postman_previewlanguage' and value == "":
            result[key] = None
        elif isinstance(value, dict):
            result[key] = fix_preview_language(value)
        elif isinstance(value, list):
            result[key] = [fix_preview_language(item) if isinstance(item, dict) else item for item in value]
        else:
            result[key] = value
    
    return result

def sanitize_file(file_path: Path) -> bool:
    """Sanitize a single Postman file and return True if changes were made."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Fix _postman_previewlanguage fields first (before validation)
        data = fix_preview_language(data)
        
        # Validate the file before sanitizing
        if file_path.name.endswith('.postman_collection.json'):
            # Perform basic structural validation without relying on the broken schema
            if not validate_collection_structure(data):
                return False
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