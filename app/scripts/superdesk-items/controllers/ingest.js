define(['angular', 'moment'], function(angular, moment) {
    'use strict';

    return ['$scope', 'superdesk', 'workqueue', '$location', '$filter',
    function($scope, superdesk, queue, $location, $filter) {
        $scope.items = superdesk.data('ingest', {
            sort: ['firstcreated', 'desc'],
            filters: ['provider'],
            max_results: 25
        });

        $scope.queue = queue;

        $scope.openEditor = function() {
            superdesk.intent('edit', 'ingest', queue.active);
        };

        $scope.search = {
            type: {
                text: true,
                audio: false,
                video: false,
                picture: false,
                graphic: false,
                composite: false
            },
            general: {
                provider: null,
                creditline: null,
                place: null,
                urgency: {
                    from: null,
                    to: null
                },
                versioncreated: {
                    from: null,
                    to: null
                }
            }
        };

        //helper variables to handle large number of changes
        $scope.versioncreated = {
            startDate: null,
            endDate: null,
            init: false
        };
        $scope.urgency = {
            from: 1,
            to: 5
        };

        var createFilters = function() {

            var filters = [];

            function chainRange(obj, key) {
                if (obj !== null && obj.from !== null && obj.to !== null) {
                    var rangefilter = {};
                    rangefilter[key] = {from: obj.from, to: obj.to};
                    filters.push({range: rangefilter});
                }
            }

            function chain(val, key) {
                if (val !== null && val !== '') {
                    var t = {};
                    t[key] = val;
                    filters.push({term: t});
                }
            }

            //process content type
            var contenttype = [];
            _.forEach($scope.search.type, function(checked, key) {
                if (checked) {
                    contenttype.push(key);
                }
            });

            //add content type filters as OR filters
            if (contenttype.length > 0) {
                filters.push({terms: {type: contenttype}});
            }

            //process general filters
            _.forEach($scope.search.general, function(val, key) {
                if (_.isObject(val)) {
                    chainRange(val, key);
                } else {
                    chain(val, key);
                }
            });

            //do filtering
            $location.search('filter', angular.toJson({and: filters}));
        };

        var createFiltersWrap = _.throttle(createFilters, 1000);
        $scope.$watch('search', function() {
            createFiltersWrap();
        }, true);    //deep watch

        //date filter handling
        $scope.$watch('versioncreated', function(newVal) {
            if (newVal.init === true) {
                if (newVal.startDate !== null && newVal.endDate !== null) {
                    var start = $filter('dateString')(newVal.startDate);
                    var end = $filter('dateString')(newVal.endDate);
                    $scope.search.general.versioncreated = {from: start, to: end};
                }
            }
        });

        //urgency filter handling
        function handleUrgency(urgency) {
            var ufrom = Math.round(urgency.from);
            var uto = Math.round(urgency.to);
            if (ufrom !== 1 || uto !== 5) {
                $scope.search.general.urgency.from = ufrom;
                $scope.search.general.urgency.to = uto;
            }
        }

        var handleUrgencyWrap = _.throttle(handleUrgency, 2000);

        $scope.$watchCollection('urgency', function(newVal) {
            handleUrgencyWrap(newVal);
        });

    }];
});
