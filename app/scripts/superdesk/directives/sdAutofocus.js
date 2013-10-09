define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    angular.module('superdesk.directives')
        .directive('sdAutofocus', function() {
            return {
                link: function($scope, element, attrs) {
                    element.focus();
                }
            };
        });
});
