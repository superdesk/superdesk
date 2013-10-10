define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    /**
    * sdAutoFocus automatically focuses on an element on page render.
    *
    * Usage:
    * <input sd-auto-focus>
    */
    angular.module('superdesk.directives')
        .directive('sdAutoFocus', function() {
            return {
                link: function($scope, element, attrs) {
                    element.focus();
                }
            };
        });
});
