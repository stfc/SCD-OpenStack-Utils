# Cloud Slack Workspace App
## About
Using Slack's Bolt for Python library here I have developed a Slack Application currently running in the Cloud Slack Workspace.<br>
This application is designed to help promote the closing of GitHub pull requests either by getting them approved and merged or closed when they go stale.<br>
In principle, the app will notify authors about their pull requests until they are closed.<br>
### Deployment
In this repository there is a **Dockerfile** this should build an image that will run the application in a Python container.<br>
Deployment steps as follows:
1. Pull the image locally from the Harbor repo `stfc-cloud/cloud-chatops`.
2. Create the 4 files in the requirements section.
3. Start a docker container using that image.
4. Copy the files to `/slack_app` on the container.
5. You may need to restart the container.
### Functionality
As of current, the application gets all open pull requests from any Cloud owned repository and will send a message to our pull-request channel about each pull request notifying the author.<br>
The app runs on an asynchronous loop scheduling each reminder to be sent out on days of our catch-ups (Monday, Wednesday and Friday).<br>
On Mondays the application will mention users with **@** as to notify them directly. However, on the other 2 days authors will not be mentioned as to not spam people.<br>
### Requirements:
The following files need to be present in the working directory of the application.<br>
- **repos.csv**: A list of repositories owned by `stfc` (e.g. `repo1,repo2,repo3`).<br>
- **user_map.json**: A dictionary of GitHub usernames to Slack Member IDs (e.g. `{"khalford":"ABC123"}`).<br>
- **secrets.json**: A dictionary of token names to token values (e.g. `{"SLACK_APP_TOKEN":"123ABC"}`). <br>
- **maintainer.txt**: A text file containing the maintainer users Slack Member ID.

For `secrets.json` the following token structure can be used:<br>
```json
{
  "SLACK_BOT_TOKEN": "ABC123",
  "SLACK_APP_TOKEN": "CDE456",
  "GITHUB_TOKEN": "FGH789",
  "INFLUX_TOKEN": "IJK012"
}
```
