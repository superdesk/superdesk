#!/bin/bash
cd /opt/superdesk/client &&
grunt server --server='http://localhost:5000/api' --ws='ws://localhost:5100' &
cd /opt/superdesk &&
python3 manage.py users:create -u admin -p admin -e 'admin@example.com' --admin &&
bash ./scripts/fig_wrapper.sh honcho start
