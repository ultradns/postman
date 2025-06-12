# Postman Collection Scripts

This directory contains utility scripts used in our CI/CD workflows to maintain and validate our Postman collections.

## Scripts Overview

### `validate_postman.py`

Validates Postman collection and environment files to ensure they:
- Are valid JSON
- Conform to the Postman collection schema (v2.1.0)
- Have required fields for environment files
- Can be processed by our sanitization script

Usage:
```bash
python validate_postman.py <directory>
```

### `sanitize_postman.py`

Cleans up Postman collection and environment files by:
- Removing metadata properties (IDs, timestamps, etc.)
- Stripping version numbers from collection/environment names
- Ensuring consistent JSON formatting
- Validating against the Postman schema

Usage:
```bash
python sanitize_postman.py <directory>
```

### `ptoa_postprocess.py`

Converts Postman collections to OpenAPI specifications by:
1. Using the Postman API to transform a collection into OpenAPI format
2. Post-processing the OpenAPI definition to:
   - Remove request bodies from GET/DELETE operations
   - Replace variable servers with a fixed URL
   - Ensure proper schema definitions for parameters
   - Add missing operationIds
   - Wrap request body examples in schemas
   - Add default response schemas
   - Remove Postman metadata

Usage:
```bash
# Requires environment variables:
export POSTMAN_API_KEY="your-api-key"
export POSTMAN_COLLECTION_ID="your-collection-id"
python ptoa_postprocess.py
```

## Dependencies

These scripts require Python 3.x and the following packages:
- `requests`
- `jsonschema`
- `ruamel.yaml` (for `ptoa_postprocess.py`)

You can install the dependencies using:
```bash
pip install -r requirements.txt
``` 