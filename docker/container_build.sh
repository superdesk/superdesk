#!/bin/bash
set -eux

INSTANCE="${1:-}"

[ -z "$INSTANCE" ] && {
	echo "
Usage: $0 INSTANCE_NAME
       $0 master
"
	exit 1
}

SCRIPT_DIR=$(readlink -e $(dirname "$0"))
BAMBOO_DIR=$(readlink -e $SCRIPT_DIR/..)
SERVER_RESULTS_DIR=$BAMBOO_DIR/results/server
CLIENT_RESULTS_DIR=$BAMBOO_DIR/results/client
SCREENSHOTS_DIR=/opt/screenshots/$INSTANCE/$(date +%Y%m%d-%H%M%S)/

# allow some bamboo values to be unfilled
RUN_E2E=${bamboo_RUN_E2E:=1}

# install script requirements
virtualenv $SCRIPT_DIR/env
set +u
. $SCRIPT_DIR/env/bin/activate
set -u
pip install -q -r $SCRIPT_DIR/requirements.txt || exit 1


export COMPOSE_PROJECT_NAME=build_$INSTANCE
export COMPOSE_HTTP_TIMEOUT=600


# {{{
echo "===pre clean-up:"
cd $SCRIPT_DIR

set +e
docker-compose kill
docker-compose rm -fv

sudo rm -r $BAMBOO_DIR/data/
mkdir -p $BAMBOO_DIR/data/{mongodb,elastic,redis}

sudo rm -r $BAMBOO_DIR/results/ ;

#sudo rm -r $SCREENSHOTS_DIR ;
#mkdir -p $SCREENSHOTS_DIR ;

set -e
echo "+++pre clean-up done"
# }}}

function post_clean_up {
	echo "===post clean-up:"
	set +e
		docker-compose kill;
		killall chromedriver;
	set -e
	test ${CODE:=0} -gt 0 && (
		echo "===removing failed containers:"
		docker-compose rm -fv;
	) ;
	echo "+++post clean-up done"
}
trap post_clean_up EXIT SIGHUP SIGINT SIGTERM


# {{{
echo "===updating containers:"
bamboo_buildKey="${bamboo_buildKey:-}"
if [ -n $bamboo_buildKey ]
	then
		# reset repo files' dates:
		cd $BAMBOO_DIR
		find ./ -print0 | grep -vzZ .git/ | xargs -0 touch -t 200001010000.00
fi
# build container:
cd $SCRIPT_DIR
docker-compose pull
docker-compose build
docker-compose up -d
# }}}

# don't give if some of the tests failed:

if [[ $RUN_E2E = 1 ]] ; then
	# create admin user:
	docker-compose run superdesk ./scripts/fig_wrapper.sh python3 manage.py users:create -u admin -p admin -e 'admin@example.com' --admin
	echo "+++ new user has been created"

	# run e2e tests:
	(
		cd $BAMBOO_DIR
		docker kill protractor_${INSTANCE}_run || true
		docker rm -fv protractor_${INSTANCE}_run || true
		docker build -f ${BAMBOO_DIR}/docker/protractor.Dockerfile -t protractor_${INSTANCE} ./
		docker run --link build$(sed 's/[-_/.:]//g' <<< $INSTANCE)_superdesk_1:superdesk -d -v $CLIENT_RESULTS_DIR:/opt/superdesk-client/e2e-test-results --name=protractor_${INSTANCE}_run protractor_${INSTANCE}
		set +e
		docker exec protractor_${INSTANCE}_run bash -c "\
			cd /opt/superdesk-client/node_modules/superdesk-core/spec/ \
			&& bash ./fit_tests.sh \
			&& cd /opt/superdesk-client \
			&& xvfb-run ./node_modules/.bin/protractor-flake \
				--node-bin node --max-attempts=3 -- protractor-conf.js \
				--stackTrace --verbose \
				--baseUrl 'http://superdesk' \
				--params.baseBackendUrl 'http://superdesk/api' \
				--params.username 'admin' \
				--params.password 'admin' \
				--specs=./node_modules/superdesk-core/spec/*" \
		|| sleep 10000
		CODE="$?"
		set -e
		docker kill protractor_${INSTANCE}_run || true
		docker rm -fv protractor_${INSTANCE}_run || true
		#mv $BAMBOO_DIR/client/screenshots $SCREENSHOTS_DIR
			#echo "!!! Screenshots were saved to $SCREENSHOTS_DIR"
		#true
	)
fi

exit 0
