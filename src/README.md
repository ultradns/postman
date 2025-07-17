# UltraDNS Postman Collection Files

This directory contains the Postman collection and environment files for the UltraDNS API.

## Files

- `UDNS.postman_collection.json`: The main collection containing all UltraDNS API requests
- `UDNS.postman_environment.json`: A template environment file with variables needed for the collection

## Importing the Files

You have several options to import these files into Postman:

### Option 1: Import from Local Files
1. Clone this repository
2. Open Postman
3. Go to **File** > **Import**
4. Drag the JSON files from this directory into Postman

### Option 2: Import from GitHub
1. Open the file you want to import in GitHub
2. Click the "Raw" button
3. Copy the URL from your browser
4. In Postman, go to **File** > **Import**
5. Paste the URL into the "Import from Link" field

### Option 3: Fork from Public Workspace (Recommended)
The easiest way to get started is to:
1. Visit our [public workspace](https://www.postman.com/digicertultradns/ultradns-public-workspace/overview)
2. Fork the collection to your own workspace
3. Create an environment and set up your credentials

## Environment Setup

After importing the collection, you'll need to:

1. **Set your credentials**
   - Define the following environment variables:

     * `username` – your UDNS username
     * `password` – your UDNS password

2. **Manually obtain your token (first time)**
   - In Postman:

     * Open the **Authorization** tab at the collection level
     * Click **"Get New Access Token"**, then **"Use Token"**

3. **Token refresh**
   - After the initial token is retrieved, Postman will automatically refresh it when needed—provided the refresh token remains valid.

For more detailed information about using the collection, please refer to the [main README](../README.md). 