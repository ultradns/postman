#!/usr/bin/env python3
"""
scripts/ptoa_postprocess.py

1. Uses the Postman API to convert an existing collection into an OpenAPI definition.
   (GET https://api.getpostman.com/collections/<COLLECTION_ID>/transformations)
2. Parses the returned JSON (the `output` field) into a Python dict.
3. Patches the OpenAPI dict:
   - Removes any requestBody from GET or DELETE operations.
   - Replaces "{{...}}" servers with a fixed URL.
   - Ensures each path parameter has schema: { type: string }.
   - Adds an operationId if missing.
   - Wraps requestBody examples into a minimal schema (for POST/PUT/PATCH only).
   - Injects a default { type: object } schema into responses that lack one.
   - Recursively strips any Postman metadata keys (_postman_id, _exporter_id).
4. Dumps the final spec to `spec/udns_openapi.yml` (YAML).
"""

import os
import sys
import json
import requests
from pathlib import Path
from ruamel.yaml import YAML

# ─── CONFIGURATION ────────────────────────────────────────────────────────────────

# Where to write the final patched YAML:
PATCHED_YAML_PATH = Path("spec/udns_openapi.yml")

# Actual server URL to use for the OpenAPI spec.
PREFERRED_SERVER = "https://api.ultradns.com"

# ──────────────────────────────────────────────────────────────────────────────────


def fetch_openapi_from_postman(api_key: str, collection_id: str) -> dict:
    """
    Call the Postman API to convert a collection into an OpenAPI spec.
    Returns the parsed OpenAPI dict.
    """
    url = f"https://api.getpostman.com/collections/{collection_id}/transformations"
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }
    print(f"⏳ Fetching OpenAPI transformation for collection {collection_id} …")
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"❌ Postman API returned {resp.status_code}:\n{resp.text}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    # The API returns {"output": "<stringified JSON>"}
    if "output" not in data:
        print("❌ Unexpected response: no 'output' field", file=sys.stderr)
        sys.exit(1)

    # `output` is a JSON string; parse it into a dict
    try:
        openapi_dict = json.loads(data["output"])
    except json.JSONDecodeError as e:
        print("❌ Failed to parse 'output' JSON:", e, file=sys.stderr)
        sys.exit(1)

    print("✅ Received raw OpenAPI definition from Postman API")
    return openapi_dict


def deep_clean(obj):
    """
    Recursively remove any keys named "_postman_id" or "_exporter_id".
    """
    if isinstance(obj, dict):
        obj.pop("_postman_id", None)
        obj.pop("_exporter_id", None)
        for v in obj.values():
            deep_clean(v)
    elif isinstance(obj, list):
        for item in obj:
            deep_clean(item)


def patch_openapi(doc: dict):
    """
    Mutate the OpenAPI dict in place to:
      1. Remove any requestBody from GET or DELETE operations.
      2. Replace servers with a single PREFERRED_SERVER.
      3. Ensure each parameter has schema: { type: string }.
      4. Add operationId if missing (derived from method+path).
      5. Wrap requestBody examples into a minimal schema if no schema present (for POST/PUT/PATCH).
      6. Inject default { type: object } schema into response contents that lack one.
      7. Recursively remove any Postman metadata (_postman_id, _exporter_id).
    """

    # 1) Remove requestBody from GET/DELETE operations
    for path_key, path_item in doc.get("paths", {}).items():
        # We iterate over a copy of the methods because we may delete keys
        for method in list(path_item.keys()):
            if method.lower() in {"get", "delete"}:
                if "requestBody" in path_item[method]:
                    del path_item[method]["requestBody"]
                    print(f"   ✔ Removed requestBody from {method.upper()} {path_key}")

    # 2) Replace servers array with a single fixed URL
    if "servers" in doc and isinstance(doc["servers"], list):
        doc["servers"] = [{"url": PREFERRED_SERVER, "description": "Primary UltraDNS API"}]
        print(f"   ✔ Replaced servers with {PREFERRED_SERVER}")

    # 3) Walk through paths → methods → operations
    paths = doc.get("paths", {})
    for path_key, path_item in paths.items():
        for method, operation in path_item.items():
            if method.lower() not in {"get", "post", "put", "delete", "patch", "options", "head"}:
                continue

            # 3a) Add operationId if missing
            if not operation.get("operationId"):
                raw_id = f"{method}_{path_key}"
                safe_id = (
                    raw_id.replace("/", "_")
                          .replace("{", "_")
                          .replace("}", "_")
                          .replace("__", "_")
                          .strip("_")
                )
                operation["operationId"] = safe_id
                print(f"   ✔ Added operationId '{safe_id}' for {method.upper()} {path_key}")

            # 3b) Ensure each parameter has a schema and required for path params
            params = operation.get("parameters", [])
            if not isinstance(params, list):
                params = []
                operation["parameters"] = params

            for p in params:
                # Remove leftover Postman metadata
                p.pop("_postman_id", None)
                p.pop("_exporter_id", None)

                if not p.get("schema"):
                    p["schema"] = {"type": "string"}
                    print(f"   ✔ Added schema:type=string for param '{p.get('name')}' "
                          f"in {method.upper()} {path_key}")

                if p.get("in") == "path":
                    p["required"] = True

            # 3c) Only wrap requestBody for methods that allow a body (POST, PUT, PATCH)
            if method.lower() in {"post", "put", "patch"}:
                req_body = operation.get("requestBody", {}).get("content", {}).get("application/json")
                if req_body is not None:
                    if not req_body.get("schema"):
                        if req_body.get("example") is not None:
                            req_body["schema"] = {
                                "type": "object",
                                "additionalProperties": True,
                                "example": req_body["example"],
                            }
                            req_body.pop("example", None)
                            print(f"   ✔ Wrapped example in requestBody schema for {method.upper()} {path_key}")
                        else:
                            req_body["schema"] = {"type": "object", "additionalProperties": True}
                            print(f"   ✔ Added empty requestBody schema for {method.upper()} {path_key}")

            # 3d) Responses: ensure a default schema for application/json if missing
            for status_code, resp_obj in operation.get("responses", {}).items():
                content = resp_obj.get("content", {}).get("application/json")
                if content is not None and not content.get("schema"):
                    content["schema"] = {"type": "object", "additionalProperties": True}
                    print(f"   ✔ Added default response schema for status {status_code} "
                          f"on {method.upper()} {path_key}")

    # 4) Deep-clean Postman metadata (_postman_id, _exporter_id)
    deep_clean(doc)
    print("   ✔ Stripped any _postman_id / _exporter_id fields")


def save_as_yaml(doc: dict, out_path: Path):
    """
    Dump the Python dict `doc` into `out_path` as YAML.
    """
    yaml = YAML()
    yaml.width = 120
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        yaml.dump(doc, f)
    print("✅ Patched OpenAPI written to", out_path)


def main():
    api_key = os.getenv("POSTMAN_API_KEY")
    coll_id = os.getenv("POSTMAN_COLLECTION_ID")
    if not api_key or not coll_id:
        print("❌ You must set POSTMAN_API_KEY and POSTMAN_COLLECTION_ID environment variables.", file=sys.stderr)
        sys.exit(1)

    # 1) Fetch raw OpenAPI from Postman’s transformation endpoint
    raw_doc = fetch_openapi_from_postman(api_key, coll_id)

    # 2) Patch in place to remove invalid requestBodies and fix schemas
    patch_openapi(raw_doc)

    # 3) Save the final, Swagger-compatible YAML
    save_as_yaml(raw_doc, PATCHED_YAML_PATH)


if __name__ == "__main__":
    main()
