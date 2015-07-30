#!/bin/bash

[ -z "$1" ] &&
echo "Usage: $0 INSTANCE_NAME" &&
echo "       $0 master" &&
exit 1

INSTANCE="$1"

SCRIPT_DIR=$(readlink -e $(dirname "$0"))
BAMBOO_DIR=$(readlink -e $SCRIPT_DIR/..)
SERVER_RESULTS_DIR=$BAMBOO_DIR/results/server
CLIENT_RESULTS_DIR=$BAMBOO_DIR/results/client
SCREENSHOTS_DIR=/opt/screenshots/$INSTANCE/$(date +%Y%m%d-%H%M%S)/

# install script requirements
virtualenv -p python2 $SCRIPT_DIR/env &&
. $SCRIPT_DIR/env/bin/activate &&
pip install -q -r $SCRIPT_DIR/requirements.txt || exit 1


export COMPOSE_PROJECT_NAME=build_$INSTANCE


# clean-up container stuff:
cd $SCRIPT_DIR &&
sudo rm -r $BAMBOO_DIR/data/
mkdir -p $BAMBOO_DIR/data/{mongodb,elastic,redis}

# cleanup tests' results:
sudo rm -r $BAMBOO_DIR/results/
mkdir -p $SERVER_RESULTS_DIR/{unit,behave} &&
mkdir -p $CLIENT_RESULTS_DIR/unit &&
sudo rm -r $SCREENSHOTS_DIR
mkdir -p $SCREENSHOTS_DIR

if [ -n $bamboo_buildKey ]
	then
		# reset repo files' dates:
		cd $BAMBOO_DIR
		find ./ -print0 | grep -vzZ .git/ | xargs -0 touch -t 200001010000.00
fi

# build container:
cd $SCRIPT_DIR &&
docker-compose pull &&
docker-compose build &&
docker-compose migrate-to-labels &&
docker-compose up -d --x-smart-recreate -t 600 &&

(
	# run backend unit tests:
	docker-compose run backend ./scripts/fig_wrapper.sh nosetests -sv --with-xunit --xunit-file=./results-unit/unit.xml --logging-level ERROR ;

	# run backend behavior tests:
	docker-compose run backend ./scripts/fig_wrapper.sh behave --junit --junit-directory ./results-behave/  --format progress2 --logging-level ERROR ;

	# run frontend unit tests:
	docker-compose run frontend bash -c "grunt bamboo && mv test-results.xml ./unit-test-results/" ;
	true
) &&

# create admin user:
docker-compose run backend ./scripts/fig_wrapper.sh python3 manage.py users:create -u admin -p admin -e 'admin@example.com' --admin=true &&
echo "+++ new user has been created" &&

# run e2e tests:
(
	cd $BAMBOO_DIR/client &&
	sh $SCRIPT_DIR/run_e2e_tests.sh ;
	mv $BAMBOO_DIR/client/e2e-test-results $CLIENT_RESULTS_DIR/e2e
	mv $BAMBOO_DIR/client/screenshots $SCREENSHOTS_DIR &&
		echo "!!! Screenshots were saved to $SCREENSHOTS_DIR"
	true
) &&
CODE="$?"

echo "===clean-up:"
(
	docker-compose stop;
	docker-compose kill;
	killall chromedriver;
);
echo "+++clean-up done"

exit $CODE
