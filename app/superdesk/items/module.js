define([
    'angular',
    'superdesk/items/controllers/list'
], function(angular) {
    'use strict';

    angular.module('superdesk.items', []).
        config(function($routeProvider) {
            $routeProvider.
                when('/', {
                    controller: require('superdesk/items/controllers/list'),
                    templateUrl: 'superdesk/items/views/list.html'
                });
        });
});
