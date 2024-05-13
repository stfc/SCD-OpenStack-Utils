<h1>Cloud Slack Workspace App</h1>
<h3>About</h3>
Using Slack's Bolt for Python library here I have developed a Slack Application currently running in the Cloud Slack Workspace. This application is designed to help promote the closing of GitHub pull requests either by getting them approved and merged or closed when they go stale. In principal the app will notify authors about their pull requests until they are closed.<br>
<h3>Functionality</h3>
As of current, the application gets all open pull requests from any Cloud owned repository and will send a message to our pull-request channel about each pull request notifying the author.<br>
The app runs on an asynchronous loop scheduling each reminder to be sent out on days of our catch-ups (Monday, Wednesday and Friday).<br>
On Mondays the application will mention users with "@" as to notify them directly. However, on the other 2 days authors will not be mentioned as to not spam people.<br>
