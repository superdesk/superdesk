define([
    'angular'
], function(angular) {
    'use strict';

    var testService = angular.module('superdesk.services.test', []);
    
    testService.factory('testService', function(){
        return function() {
            console.log('test');
        };
    });
});