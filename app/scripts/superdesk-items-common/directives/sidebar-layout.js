define(['angular', 'require'], function(angular, require) {
    'use strict';

    angular.module('superdesk.items-common.directives')
        .directive('sdSidebarLayout', ['$location', '$filter', function($location, $filter) {
            return {
                transclude: true,
                templateUrl: require.toUrl('../views/sidebar.html'),
                controller: ['$scope', function($scope) {

                    $scope.$watchCollection('items', function() {
                        if ($scope.items && $scope.items._facets !== undefined) {
                            _.forEach($scope.items._facets.type.terms, function(type) {
                                _.extend(_.first(_.where($scope.contenttype, {term: type.term})), type);
                            });
                        }
                    });

                    $scope.contenttype = [
                        {
                            term: 'text',
                            checked: false,
                            count: 0
                        },
                        {
                            term: 'audio',
                            checked: false,
                            count: 0
                        },
                        {
                            term: 'video',
                            checked: false,
                            count: 0
                        },
                        {
                            term: 'picture',
                            checked: false,
                            count: 0
                        },
                        {
                            term: 'graphic',
                            checked: false,
                            count: 0
                        },
                        {
                            term: 'composite',
                            checked: false,
                            count: 0
                        }
                    ];

                    $scope.setContenttypeFilter = function() {
                        var contenttype = _.map(_.where($scope.contenttype, {'checked': true}), function(t) {
                            return t.term;
                        });
                        if (contenttype.length === 0) {
                            $location.search('type', null);
                        } else {
                            $location.search('type', JSON.stringify(contenttype));
                        }
                    };

                     /*
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
                        var contenttype = _.map(_.where($scope.search.type, {'checked': true}), function(t) { return t.term; });

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

                        //process subject filters
                        if ($scope.search.subjects.length > 0) {
                            filters.push({terms: {'subject.name': $scope.search.subjects, execution: 'and'}});
                        }

                        //process place filters
                        if ($scope.search.places.length > 0) {
                            filters.push({terms: {'place.name': $scope.search.places, execution: 'and'}});
                        }

                        //do filtering
                        if (filters.length > 0) {
                            $location.search('filter', angular.toJson({and: filters}));
                        } else {
                            $location.search('filter', null);
                        }

                    };

                    //date filter handling
                    $scope.$watch('versioncreated', function(newVal) {
                        if (newVal.init === true) {
                            if (newVal.startDate !== null && newVal.endDate !== null) {
                                var start = $filter('1')(newVal.startDate);
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

                    $scope.addSubject = function(item) {
                        if (!_.contains($scope.search.subjects, item.term.toLowerCase())) {
                            $scope.search.subjects.push(item.term);
                        }
                    };

                    $scope.removeSubject = function(item) {
                        $scope.search.subjects = _.without($scope.search.subjects, item);
                    };

                    $scope.addPlace = function(item) {
                        if (!_.contains($scope.search.places, item.term.toLowerCase())) {
                            $scope.search.places.push(item.term);
                        }
                    };

                    $scope.removePlace = function(item) {
                        $scope.search.places = _.without($scope.search.places, item);
                    };
                    */
                }]
            };
        }]);
});
