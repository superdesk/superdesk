define(['lodash'], function(_) {
    'use strict';

    PlanningDashboardController.$inject = ['$scope'];
    function PlanningDashboardController($scope) {

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

    	$scope.items = [
    		{
    			headline: 'Et harum quidem rerum facilis est et expedita distinctio',
    			description: 'Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam' +
    			'nisi ut aliquid ex ea commodi consequatu',
    			duedate: 'Today at 15:30',
    			tasks: 'Story,Photo',
    			comments: 2,
    			attachments: 3,
    			links: 2
    		},
    		{
    			headline: ' Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates',
    			description: 'Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci' +
    			'velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem.',
    			duedate: 'Today at 16:30',
    			tasks: 'Story',
    			comments: 4,
    			attachments: 1
    		}
    	];
    }

    return PlanningDashboardController;
});
