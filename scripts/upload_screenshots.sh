#!/bin/bash

CLIENTID='3e7a4deb7ac67da'
IMAGES=$SCREENSHOT_DIR/*.png

for img in in $IMAGES; do
    echo -e "\n"
    res=$(curl -sH "Authorization: Client-ID $CLIENTID" -F "image=@$img" "https://api.imgur.com/3/upload")
    echo $res | grep -qo '"status":200' && link=$(echo $res | sed -e 's/.*"link":"\([^"]*\).*/\1/' -e 's/\\//g')
    echo $link
done