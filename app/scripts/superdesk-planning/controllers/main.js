define(['lodash'], function(_) {
    'use strict';

    PlanningDashboardController.$inject = ['$scope', 'mockItems'];
    function PlanningDashboardController($scope, mockItems) {

    	$scope.newItem = {
            headline: null
        };
    	$scope.selectedItem = null;

    	$scope.addItem = function() {
    		$scope.items.unshift(_.clone($scope.newItem));
    		$scope.newItem.headline = null;
    	};

    	$scope.preview = function(item) {
    		$scope.selectedItem = item;
    	};

    	$scope.items = mockItems.list;
    }

    return PlanningDashboardController;
});
