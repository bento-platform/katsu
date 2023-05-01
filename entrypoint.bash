#!/bin/bash

cd /app || exit

# Create bento_user + home
source /create_service_user.bash

# Create /app/tmp if it doesn't exist (say, in the local mount of the code)
mkdir -p /app/tmp

# Fix permissions on /app/tmp and /env
chown -R bento_user:bento_user /app/tmp
chmod -R o-rwx /app/tmp  # Remove all access from others

# Drop into bento_user from root and execute the CMD specified for the image
exec gosu bento_user "$@"
