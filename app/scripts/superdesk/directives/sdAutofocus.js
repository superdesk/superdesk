define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    angular.module('superdesk.directives')
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
