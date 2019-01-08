cd /opt/superdesk/client-core &&
npm link &&
cd /opt/superdesk/client &&
npm link superdesk-core &&
npm install &&
grunt server --server='http://localhost:5000/api' --ws='ws://localhost:5100' &

cd /opt/superdesk &&
python3 manage.py users:create -u admin -p admin -e 'admin@example.com' --admin &&
bash ./scripts/fig_wrapper.sh honcho start
