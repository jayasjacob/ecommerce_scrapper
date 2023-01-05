#!/bin/bash


#Force file synchronization and lock writes
mongo admin --eval "printjson(db.fsyncLock())"

MONGORESTORE_PATH="/usr/bin/mongorestore"

MONGO_DATABASE="Revmeup" # database name

tar -xf ./$HOSTNAME-*.tar #--strip-components=1
MONGO_BACKUP_PATH="$HOSTNAME-*"
MONGORESTORE_PATH --db MONGO_DATABASE --drop MONGO_BACKUP_PATH

#Unlock database writes
mongo admin --eval "printjson(db.fsyncUnlock())"
#Delete local files
#rm -rf mongodb-"$HOSTNAME"-"$TIMESTAMP".tar
#rm -rf mongodb-*   #Remove From Disk
