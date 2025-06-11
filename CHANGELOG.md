# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions workflow to trigger a release when a new tag is pushed

## [0.1.1] - 2025-06-11

### Added
- GitHub Actions workflow to convert Postman collection to OpenAPI schema after publish

### Changed
- Appending version to the collection and environment names

### Fixed
- Issue with the `HASH` placeholder value needing to be blanked out of environment before collection could be used

## [0.1.0] - 2025-06-10

### Added
- GitHub Actions workflow to validate Postman collection schema on pull requests
- GitHub Actions workflow to sanitize collection data on push to main branch
- GitHub Actions workflow to automatically publish collections to Postman workspace on release
- New API endpoints for DNS record testing:
  - GET endpoint for CNAME record validation
  - GET endpoint for A record validation
- Python utility scripts in `scripts/` directory:
  - `validate_postman.py`: Validates Postman collection schemas
  - `sanitize_postman.py`: Sanitizes collection data
  - `ptoa_postprocess.py`: Converts Postman collections to OpenAPI format
- OpenAPI specification in `spec/` directory, automatically generated from Postman collections