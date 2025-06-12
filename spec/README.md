# OpenAPI Specification

This directory contains the OpenAPI (formerly Swagger) specification for the UltraDNS API. The specification is automatically generated from our Postman collection during releases using the `ptoa_postprocess.py` script.

## About OpenAPI

The OpenAPI Specification (OAS) defines a standard, programming language-agnostic interface description for REST APIs. This allows both humans and computers to discover and understand the capabilities of a service without requiring access to source code, additional documentation, or inspection of network traffic.

## Specification File

- `udns_openapi.yml`: The OpenAPI 3.0 specification for the UltraDNS API

## Documentation

For more information about the OpenAPI Specification:

- [OpenAPI Specification Documentation](https://swagger.io/specification/)
- [OpenAPI Initiative](https://www.openapis.org/)
- [OpenAPI Tools](https://openapi.tools/)

## Tools

You can use various tools to work with the OpenAPI specification:

- [Swagger Editor](https://editor.swagger.io/) - Edit and visualize the specification
- [Swagger UI](https://swagger.io/tools/swagger-ui/) - Generate interactive API documentation
- [OpenAPI Generator](https://openapi-generator.tech/) - Generate client libraries, server stubs, and documentation

## Generation

The OpenAPI specification is automatically generated from our Postman collection using the `ptoa_postprocess.py` script in the `scripts` directory. The script:

1. Uses the Postman API to convert the collection to OpenAPI format
2. Post-processes the specification to ensure it follows best practices
3. Saves the result as YAML in this directory

For more details about the generation process, see the [scripts README](../scripts/README.md). 