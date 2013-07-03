define([
    'angular',
    'superdesk/items/controllers/list'
], function(angular) {
    'use strict';

    var items = angular.module('superdesk.items', []);
    items.config(function($routeProvider) {
        $routeProvider.
            when('/', {
                controller: require('superdesk/items/controllers/list'),
                templateUrl: 'superdesk/items/views/list.html'
            });
    });
});
