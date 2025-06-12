# Contributing to UDNS Postman Collection

Thank you for your interest in contributing to the UltraDNS Postman collection! This document provides guidelines and instructions for contributing to this repository.

## Table of Contents
- [Introduction & Scope](#introduction--scope)
- [Getting Started](#getting-started)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Review Process](#review-process)
- [Release Process](#release-process)

## Introduction & Scope

This repository maintains the official UltraDNS Postman collection and environment files. These files provide a sample set of API requests for interacting with the UDNS API, including authentication handling, utility functions, and organized resource endpoints.

To maintain consistency and quality, all contributions should follow the steps outlined in this guide.

## Getting Started

1. **Fork the Repository**
   - Click the "Fork" button on the GitHub repository page
   - Clone your fork locally:
     ```bash
     git clone https://github.com/YOUR-USERNAME/postman.git
     cd postman
     ```

2. **Create a Branch**
   - Create a new branch for your changes:
     ```bash
     git checkout -b feature/your-feature-name
     # or
     git checkout -b bugfix/your-bugfix-name
     ```

## Making Changes

1. **Work in Postman**
   - Fork the UDNS collection into your own Postman workspace
   - Make your changes in the Postman app:
     - Add new endpoints
     - Modify existing requests
     - Update environment variables (if needed)
     - Test your changes thoroughly

2. **Export Updated Files**
   - Export your updated collection:
     - In Postman, click the collection's "..." menu
     - Select "Export"
     - Choose "Collection v2.1"
     - Save and overwrite `src/UDNS.postman_collection.json`
   - If you modified environment variables:
     - Export the environment
     - Save and overwrite `src/UDNS.postman_environment.json`

3. **Sanitize JSON Files (Optional but Recommended)**
   - Run the sanitization script to clean metadata:
     ```bash
     python scripts/sanitize_postman.py .
     ```

4. **Update CHANGELOG.md**
   - Add your changes under the **[Unreleased]** section
   - Follow the [Keep a Changelog](https://keepachangelog.com/) format:
     ```markdown
     ## [Unreleased]
     
     ### Added
     - Description of new endpoints or features
     
     ### Changed
     - Description of modifications to existing endpoints
     
     ### Fixed
     - Description of bug fixes
     ```

## Submitting Changes

1. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

2. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Select the `main` branch as the base
   - Provide a clear description of your changes
   - Reference any related issues

## Review Process

1. **Code Review**
   - Maintainers will review your PR for:
     - Correctness of API endpoints
     - Proper JSON formatting
     - Appropriate CHANGELOG entries
     - Overall contribution quality

2. **Addressing Feedback**
   - Respond to review comments
   - Make requested changes
   - Push updates to your branch

## Release Process

Once your PR is merged:

1. **Version Tagging**
   - Maintainers will create a Git tag incrementing the version in CHANGELOG.md
   - Example: `v1.2.3`

2. **Automated Release**
   - Pushing the tag triggers our release workflow
   - The workflow will:
     - Create a GitHub release and automatically update CHANGELOG.md
     - Publish the updated collection to Postman
     - Generate an OpenAPI spec file and commit it to the repository

No additional manual steps are required for the release process.

## Questions?

If you have any questions about contributing, please open an issue in the repository.

Thank you! 