define([
    'angular'
], function(angular) {
    'use strict';

    return angular.module('superdesk.directives.autofocus', [])
        /**
         * sdAutoFocus automatically focuses on an element on page render.
         *
         * Usage:
         * <input sd-auto-focus>
         */
        .directive('sdAutoFocus', function() {
            return {
                link: function($scope, element, attrs) {
                    element.focus();
                }
            };
        });
});
