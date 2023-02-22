#!/bin/bash

cd /app || exit

# Create bento_user + home
source /create_service_user.bash

# Fix permissions on /app - for developing or /app/tmp writing
chown -R bento_user:bento_user /app
chmod -R o-rwx /app/tmp  # Remove all access from others

# Drop into bento_user from root and execute the CMD specified for the image
exec gosu bento_user "$@"
