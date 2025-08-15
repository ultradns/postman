# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.1] - 2025-08-15

### Added
- Platform folder for system-related calls
  - `/version` request for testing API connectivity
  - `/status` request for checking status and auth
- Authorization folder for auth endpoints
  - Includes one request for new token and refresh
    - Separate response examples for reference
  - `refreshToken` added to environment

### Changed
- Improved CI scripts for validation and sanity

## [1.1.0] - 2025-07-17

### Changed
- Switched from a pre-request script Auth workflow to the baked in OAuth 2.0
  - This is necessary for OpenAPI spec generation, for the YAML to be fully usable out-of-box in other tools
  - In Postman, this necessitates an additional step when authentication
    - Set the `username` and `password` in your environment (same as before)
    - Go to the `Authorization` tab under the collection and click `Get New Access Token`
    - Once the initial token has been requested, Postman will handle auto-refresh (so long as the refresh token is not expired)
- Cleaned up some of the in-collection documentation to make it more tool-agnostic for te OpenAPI spoec
  - The Postman-specific functionalities will be detailed in the public workspace docs
- Updated `README`

## [1.0.1] - 2025-06-18

### Added
- Response examples for all endpoints

### Fixed
- Pre-request script for rrset delete
- Publish workflow
  - The collection was causing arg limit errors with `jq`
  - Wrote a simple Python script to handle the publishing to Postman

### Removed
- Subaccount section
  - Will create as a separate collection in the future

## [1.0.0] - 2025-06-17

### Added
- Documentation for all endpoints with no overview

### Changed
- Documentation refresh
  - Updated all root level folder descriptions
  - Moved documentation for SiteBacker endpoints from payload to overview
- Collapsed all list record by type endpoints into a single endpoint with a type parameter
- Moved "List Pools" to the Records folder
- Deleted redundant "List Zone RRSets" request from Zones folder
- Renamed "Request Report" to "Retrieve Report"
- Made "Zero Query Report" default to last 30 days when no date range specified
- Added "Documentation" section to CHANGELOG.md

### Fixed
- Commented out a couple lines to fix the pre-request script in "Create RRSet"

## [0.1.5] - 2025-06-12

### Added
- GET endpoint for MX records

## [0.1.4] - 2025-06-12

### Added
- GET endpoint for TXT records

## [0.1.3] - 2025-06-12

### Added
- GET endpoint for NS records

### Changed
- Removed redundant NS and SOA endpoints from zones folder

## [0.1.2] - 2025-06-11

### Added
- GitHub Actions workflow to trigger a release when a new tag is pushed
- GET endpoint for SOA record

### Changed
- `sanitize_postman.py` should strip out versions in the repo, this gets appended buy the `publish-postman.yml` workflow
- Environment is now named "Sample Environment"

### Fixed
- Incorrect URI in GET CNAME endpoint

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
