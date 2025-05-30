#!/usr/bin/env python3

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set

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
ENVIRONMENT_SCHEMA = "https://schema.getpostman.com/json/environment/v1.0.0/environment.json"

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
    
    modified_files = []
    for file_path in find_postman_files(directory):
        if sanitize_file(file_path):
            modified_files.append(str(file_path))
    
    if modified_files:
        print("Modified files:")
        for file in modified_files:
            print(f"- {file}")
        sys.exit(0)
    else:
        print("No files were modified")
        sys.exit(0)

if __name__ == '__main__':
    main() 