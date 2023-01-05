#!/bin/bash

#Force file synchronization and lock writes
mongo admin --eval "printjson(db.fsyncLock())"

MONGODUMP_PATH="/usr/bin/mongodump"
MONGO_DATABASE="revmeup" # database name

TIMESTAMP=$(date +%y%m%d_%H%M%S)
# shellcheck disable=SC2034
S3_BUCKET_NAME="amplify-revmeup-dev-151918-deployment" #bucket name on Amazon S3
# shellcheck disable=SC2034
S3_BUCKET_PATH="amplify-revmeup-dev-151918-deployment/mongodb-backups"

# Create backup
$MONGODUMP_PATH -d $MONGO_DATABASE

# Add timestamp to backup
mv dump mongodb-"$HOSTNAME"-"$TIMESTAMP"
tar cf mongodb-"$HOSTNAME"-"$TIMESTAMP".tar mongodb-"$HOSTNAME"-"$TIMESTAMP"

# Upload to S3
s3cmd put mongodb-$HOSTNAME-$TIMESTAMP.tar s3://$S3_BUCKET_NAME/$S3_BUCKET_PATH/mongodb-$HOSTNAME-$TIMESTAMP.tar

#Unlock database writes
mongo admin --eval "printjson(db.fsyncUnlock())"
#Delete local files
#tar -xf mongodb-"$HOSTNAME"-"$TIMESTAMP".tar --strip-components=1
rm -rf mongodb-"$HOSTNAME"-"$TIMESTAMP"
