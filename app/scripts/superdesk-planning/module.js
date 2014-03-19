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

    app
        .value('mockDataExample', {
            list: ['array1', 'array2', 'array3'],
            name: 'sample name'
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
