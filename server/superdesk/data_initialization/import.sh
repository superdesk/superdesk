#!/bin/bash

[ -z "$1" ] &&
echo "Usage: $0 DATABASE_NAME" &&
echo "       $0 superdesk" &&
exit 1

DATABASE="$1"

mongoimport --db $DATABASE --collection roles --file roles.json &&
mongoimport --db $DATABASE --collection users --file users.json &&
mongoimport --db $DATABASE --collection desks --file desks.json &&
mongoimport --db $DATABASE --collection stages --file stages.json &&
mongoimport --db $DATABASE --collection groups --file groups.json &&
mongoimport --db $DATABASE --collection vocabularies --file vocabularies.json &&

if [ $? -eq 0 ]
then echo 'Import completed successfully!'
fi 
exit $?
