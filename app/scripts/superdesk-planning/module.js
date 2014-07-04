define([
    'angular'
], function(angular) {
    'use strict';

    PlanningDashboardController.$inject = ['$scope', 'mockItems'];
    function PlanningDashboardController($scope, mockItems) {

    	$scope.newItem = {
            headline: null
        };
    	$scope.selected = {item: null};

    	$scope.addItem = function() {
    		$scope.items.unshift(_.clone($scope.newItem));
    		$scope.newItem.headline = null;
    	};

    	$scope.preview = function(item) {
    		$scope.selected.item = item;
    	};

    	$scope.items = mockItems.list;
    }

    function SdPreviewItem() {
    	return {
    		templateUrl: 'scripts/superdesk-planning/views/item-preview.html',
    		scope: {
    			origItem: '=item'
    		},
    		link: function(scope, elem) {

    			scope.$watch('origItem', resetItem);

    			scope.dirty = false;

    			scope.$watchCollection('item', function(item) {
                    scope.dirty = !angular.equals(item, scope.origItem);
                });

                scope.cancel = function() {
                    resetItem(scope.origItem);
                };

                scope.save = function() {
                	console.log('save changes');
                };

    			function resetItem(item) {
    				scope.item = _.create(item);
    			}
    		}
    	};
    }

    var app = angular.module('superdesk.planning', []);

    return app
    	.directive('sdPreviewItem', SdPreviewItem)
        .value('mockItems', {
            list: [
	    		{
	    			headline: 'Et harum quidem rerum facilis est et expedita distinctio',
	    			description: 'Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam' +
	    			'nisi ut aliquid ex ea commodi consequatu',
	    			createdon: '07:55:44, 26. June 2014',
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
	    			createdon: '08:13:20, 26. June 2014',
	    			duedate: 'Today at 16:30',
	    			tasks: 'Story',
	    			comments: 4,
	    			attachments: 1
	    		}
	    	]
        })
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/planning/', {
                    label: gettext('Planning'),
                    priority: 100,
                    beta: true,
                    controller: PlanningDashboardController,
                    templateUrl: 'scripts/superdesk-planning/views/main.html',
                    category: superdesk.MENU_MAIN,
                    reloadOnSearch: false,
                    filters: []
                });
        }]);
});
