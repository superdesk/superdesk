define([
    'angular'
], function(angular) {
    'use strict';

    var coverageTypes = ['story', 'photo', 'video', 'graphics', 'live-blogging'];

    function PlanningItem(deskId) {
        this.headline = null;
    }

    function Coverage(planningItemId) {
        this.planning_item = planningItemId;
        this.coverage_type = coverageTypes[0];
    }

    PlanningService.$inject = ['$location', 'api', 'es', 'notify', 'desks'];
    function PlanningService($location, api, es, notify, desks) {

        this.items = null;

        function getDeskFilter() {
            var currentDesk = desks.getCurrentDeskId();
            if (currentDesk) {
                return [{term: {desk: currentDesk}}];
            } else {
                return null;
            }
        }

        function getCriteria() {
            var query = es($location.search(), getDeskFilter());
            query.sort = [{firstcreated: 'desc'}];
            return {source: query};
        }

        this.query = function() {
            var criteria = getCriteria();
            return api.planning.query(criteria)
                .then(angular.bind(this, function(items) {
                this.items = items;
                return this.items;
            }));
        };

        this.create = function() {
            return new PlanningItem();
        };

        this.save = function(item, diff) {

            if (!item.desk && desks.getCurrentDeskId()) {
                item.desk = desks.getCurrentDeskId();
            }

            notify.startSaving();
            return api.planning.save(item, diff)
                .then(angular.bind(this, function() {
                    return this.query();
                }))
                .then(function(items) {
                    notify.stopSaving();
                    return items;
                });
        };
    }

    PlanningDashboardController.$inject = ['$scope', '$location', 'es', 'planning', 'desks'];
    function PlanningDashboardController($scope, $location, es, planning, desks) {

        $scope.newItem = planning.create();
        $scope.selected = {item: null};

        $scope.$watch(function() {
            return $location.search().q;
        }, reload);

        $scope.$watch(function() {
            return desks.getCurrentDeskId();
        }, reload);

    	$scope.addItem = function() {
            planning.save($scope.newItem).then(function() {
                $scope.items = planning.items;
                $scope.newItem = planning.create();
            });
    	};

    	$scope.preview = function(item) {
    		$scope.selected.item = item;
    	};

        function reload() {
            $scope.items = null;
            planning.query().then(function() {
                $scope.items = planning.items;
            });
        }
    }

    PreviewItemDirective.$inject = ['planning', 'api', 'notify', 'es'];
    function PreviewItemDirective(planning, api, notify, es) {
    	return {
    		templateUrl: 'scripts/superdesk-planning/views/item-preview.html',
    		scope: {
    			origItem: '=item'
    		},
    		link: function(scope, elem) {
                scope.item = null;
                scope.origCoverages = {};
                scope.coverages = {};
                scope.coverage = null;
                scope.userLookup = null;

                scope.$watch('origItem', function(origItem) {
                    resetItem(origItem);
                });

    			scope.$watchCollection('item', function(item) {
                    scope.dirty = !angular.equals(item, scope.origItem);
                });

                scope.cancel = function() {
                    resetItem(scope.origItem);
                };

                scope.save = function() {
                    planning.save(scope.origItem, scope.item).then(function() {
                        notify.success(gettext('Item saved.'));
                        resetItem(scope.origItem);
                    });
                };

                scope.addCoverage = function() {
                    scope.coverage = new Coverage(scope.item._id);
                };

                scope.saveCoverage = function(coverage) {
                    var promise = null;
                    if (coverage) {
                        promise = api.coverages.save(coverage)
                        .then(function(result) {
                            var index = _.findIndex(scope.origCoverages._items, {_id: result._id});
                            if (index !== -1) {
                                scope.origCoverages._items[index] = result;
                                scope.coverages._items[index] = _.cloneDeep(result);
                            }
                        });
                    } else {
                        scope.coverage.planning_item = scope.item._id;
                        promise = api.coverages.save({}, scope.coverage)
                        .then(function(result) {
                            scope.origCoverages._items.unshift(result);
                            scope.coverages._items.unshift(_.cloneDeep(result));
                        });
                    }
                    promise.then(function(result) {
                        scope.coverage = null;
                        notify.success(gettext('Item saved.'));
                    });
                };

                scope.cancelCoverage = function(coverage) {
                    if (coverage) {
                        var index = _.findIndex(scope.coverages._items, {_id: coverage._id});
                        scope.coverages._items[index] = _.cloneDeep(_.find(scope.origCoverages._items, {_id: coverage._id}));
                    } else {
                        scope.coverage = null;
                    }
                };

                scope.removeCoverage = function(coverage) {
                    api.coverages.remove(coverage)
                    .then(function(result) {
                        notify.success(gettext('Item removed.'));
                        fetchCoverages();
                    });
                };

                scope.isDirty = function(coverage) {
                    if (coverage) {
                        var dirty = false;
                        var fields = ['ed_note', 'assigned_user', 'coverage_type'];
                        var origCoverage = {};
                        if (coverage._id) {
                            origCoverage = scope.origCoverages._items[_.findIndex(scope.coverages._items, {_id: coverage._id})];
                        }
                        _.each(fields, function(field) {
                            if (origCoverage[field] !== coverage[field]) {
                                dirty = true;
                                return false;
                            }
                        });
                        return dirty;
                    }
                };

                var fetchCoverages = function() {
                    api.coverages.query({where: {planning_item: scope.item._id}})
                    .then(function(result) {
                        scope.origCoverages = result;
                        scope.coverages = _.cloneDeep(result);
                    });
                };

                var fetchUsers = function() {
                    api.users.query()
                    .then(function(result) {
                        scope.userLookup = {};
                        _.each(result._items, function(user) {
                            scope.userLookup[user._id] = user;
                        });
                    });
                };

                var resetItem = function(item) {
    				scope.item = _.create(item);
                    fetchCoverages();
                    fetchUsers();
    			};
    		}
    	};
    }

    AssigneeBoxDirective.$inject = ['api', 'desks', 'userList'];
    function AssigneeBoxDirective(api, desks, userList) {
        return {
            templateUrl: 'scripts/superdesk-planning/views/assignee-box.html',
            scope: {
                userId: '=',
                deskId: '='
            },
            link: function(scope, elem) {
                scope.open = false;
                scope.desksService = desks;
                scope.desk = null;
                scope.user = null;
                scope.search = null;

                scope.$watch('deskId', function(deskId) {
                    scope.desk = null;
                    desks.initialize().then(function() {
                        scope.desk = deskId ? desks.deskLookup[deskId] : desks.getCurrentDesk();
                    });
                });

                scope.$watch('userId', function(userId) {
                    scope.user = null;
                    desks.initialize().then(function() {
                        scope.user = desks.userLookup[userId];
                    });
                });

                scope.assign = function() {
                    scope.deskId = scope.desk._id;
                    scope.userId = scope.user ? scope.user._id : null;
                    scope.open = false;
                };
            }
        };
    }

    function CoverageTypeDirective() {
        return {
            templateUrl: 'scripts/superdesk-planning/views/coverage-type.html',
            controller: ['$scope', function($scope) {
                $scope.coverageTypes = coverageTypes;
            }]
        };
    }

    return angular.module('superdesk.planning', ['superdesk.elastic'])
    	.directive('sdPreviewItem', PreviewItemDirective)
        .directive('sdAssigneeBox', AssigneeBoxDirective)
        .directive('sdCoverageType', CoverageTypeDirective)
        .service('planning', PlanningService)
        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('planning', {
                type: 'http',
                backend: {rel: 'planning'}
            });
            apiProvider.api('coverages', {
                type: 'http',
                backend: {rel: 'coverages'}
            });
        }])
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/planning/', {
                    label: gettext('Planning'),
                    priority: 100,
                    beta: true,
                    controller: PlanningDashboardController,
                    templateUrl: 'scripts/superdesk-planning/views/planning.html',
                    category: superdesk.MENU_MAIN,
                    reloadOnSearch: false,
                    filters: []
                });
        }]);
});
