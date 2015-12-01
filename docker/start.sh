#!/bin/bash
cd /opt/superdesk/client/ && grunt template
nginx &

cd /opt/superdesk &&
bash ./scripts/fig_wrapper.sh honcho start
