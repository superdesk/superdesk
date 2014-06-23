define([
    'angular',
    'require',
    './workqueue-service',
    './controllers/main'
], function(angular, require, WorkqueueService) {
    'use strict';

    var app = angular.module('superdesk.authoring', []);
    app.service('workqueue', WorkqueueService);

    app
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/authoring/', {
                	label: gettext('Authoring'),
	                templateUrl: require.toUrl('./views/main.html'),
	                controller: require('./controllers/main'),
	                category: superdesk.MENU_MAIN,
	                beta: true
	            })
	            .activity('edit.text', {
	            	label: gettext('Edit item'),
	            	icon: 'pencil',
	            	controller: ['data', '$location', 'workqueue', function(data, $location, workqueue) {
	            		workqueue.add(data.item);
	                    $location.path('/authoring/').search({_id: data.item._id});
	                }],
	            	filters: [
	                    {action: superdesk.ACTION_EDIT, type: 'archive'}
	                ]
	            });
        }]);

    return app;
});
