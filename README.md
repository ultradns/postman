# ultradns-postman

This repository contains a set of sample requests for the UDNS API, built from hands-on experience. The aim is to provide a foundational framework that takes care of authentication and automates tasks and report retrievals using pre/post-request scripts.

## JSON File

The collection export can be found under src/UDNS.postman_collection.json. Similarly, there's an example environment under src/UDNS.postman_environment.json. Import these to Postman:

1. Go to **File**
2. Select **Import**
3. Drag the files to the application

## Authentication and Utilities

The collection-level pre-request script manages authentication and has some helper functions.

Since `utils` is defined globally by not using a declaration keyword, it is accessible to request-level scripts. This allows for the definition of reusable functions for our requests. Utility functions can be invoked like so:

```javascript
utils.functionName()
```

### Username/Password

For the pre-request script to run, you must set `username` and `password` variables containing your UDNS credentials in an environment. UDNS uses OAuth2 to generate an access token. The access token and refresh token will also be stored in your environment along with a timestamp, so the script knows when to refresh.

## Resources

The collection is organized into folders, each representing a base resource (ex: `zones`) or a specific functionality (ex: `push notifications`).

- **Zones**: Contains the DNS configuration. Some resources are not available in the latest "version" of the API, hence why "snapshot/restore" use the "v1" endpoint.

- **Tasks**: Operations that produce background tasks will return a `202` status code and have an `x-task-id` header. This ID is stored under the `currentTask` variable in the environment.

- **Reports**: After you request a report, retrieve it from the `results` endpoint using the report ID. This ID is stored in the post-request script, similar to tasks.

- **Webhook**: A set of 3 requests related to UDNS's push notification feature.

- **Subaccounts**: APIs exclusive to accounts that contain child accounts. If you don't have access to this feature, they'll produce an error.

- **Records**: APIs for adding/updating/deleting RRsets for a zone.  These APIs use RRset DTO definitions and pre-request/post-request scripts for managing environment variables and POST body content.

## Bypassing Automated Authentication

To manually provide your Bearer token, go to the "Authorization" tab of the collection and modify the value. This would be necessary, as an example, to use a token produced by the subaccount authorization endpoint. Remember to revert it to the `{{accessToken}}` variable after you're done.

## Collaboration

This collection isn't meant to be definitive but is designed to be easily extensible. Contributions to expand the collection and implement more endpoints are welcomed and encouraged. The goal is for this collection to evolve as a collaborative tool.

Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on how to contribute to this project.

## License

This repo is distributed under the MIT license.
