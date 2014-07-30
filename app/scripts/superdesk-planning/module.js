define([
    'angular'
], function(angular) {
    'use strict';

    function PlanningItem(deskId) {
        this.headline = null;
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

    PreviewItemDirective.$inject = ['planning'];
    function PreviewItemDirective(planning) {
    	return {
    		templateUrl: 'scripts/superdesk-planning/views/item-preview.html',
    		scope: {
    			origItem: '=item'
    		},
    		link: function(scope, elem) {

    			scope.$watch('origItem', resetItem);

    			scope.$watchCollection('item', function(item) {
                    scope.dirty = !angular.equals(item, scope.origItem);
                });

                scope.cancel = function() {
                    resetItem(scope.origItem);
                };

                scope.save = function() {
                    planning.save(scope.origItem, scope.item).then(function() {
                        resetItem(scope.origItem);
                    });
                };

    			function resetItem(item) {
    				scope.item = _.create(item);
    			}
    		}
    	};
    }

    return angular.module('superdesk.planning', ['superdesk.elastic'])
    	.directive('sdPreviewItem', PreviewItemDirective)
        .service('planning', PlanningService)
        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('planning', {
                type: 'http',
                backend: {rel: 'planning'}
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
