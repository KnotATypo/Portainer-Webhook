# Portainer Webhook

A simple application to provide an update webhook for Portainer without paying for the Business Edition. This is 
intended to be run as a Docker container so it can be run inside Portainer itself, but it can also be run standalone.

## Configuration

```dotenv
PORTAINER_USERNAME=
PORTAINER_PASSWORD=
PORTAINER_API=
HOOK_SECRET=
```
The application requires these four environmental variables. 
- `PORTAINER_USERNAME` and `PORTAINER_PASSWORD` are the username and password of the user to authenticate to Portainer 
with. While not critical, it is recommended that you create a new user for this application.
- `PORTAINER_API` is the typical URL you use to access your instance.
- `HOOK_SCRET` is a random string used to authenticate yourself to the webhook.

If running in Docker, it is recommended to use the docker-compose.yaml found in this repo which will pull in these 
required variables from a .env file.