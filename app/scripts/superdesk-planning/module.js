define([
    'angular',
    'require',
    './controllers/main',
    './directives'
], function(angular, require) {
    'use strict';

    var app = angular.module('superdesk.planning', [
        'superdesk.planning.directives'
    ]);

    return app
        .value('mockItems', {
            list: [
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
	    	]
        })
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/planning/', {
                    label: gettext('Planning'),
                    priority: 100,
                    beta: true,
                    controller: require('./controllers/main'),
                    templateUrl: 'scripts/superdesk-planning/views/main.html',
                    category: superdesk.MENU_MAIN,
                    reloadOnSearch: false,
                    filters: []
                });
        }]);
});
