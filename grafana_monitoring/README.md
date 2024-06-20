All required environment variables can be found in env.sh and should be updated before deploying, environment variables are included in compose.yaml and will be copied to the container

# compose.yaml
Specifies the image, name, and environment variables used when arranging docker

# cloud_datasource.yaml
When grafana see this file it makes connection to the databases specified in this file

# env.sh
Stores environment variables which cannot be published onto github
User should edit and run this script to export the environment variables
