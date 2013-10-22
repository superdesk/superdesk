define([
    'angular'
], function(angular) {
    'use strict';

    angular.module('superdesk.directives')
        /**
         * sdWithParams manipulates href attribute to include current parameters.
         *
         * Usage:
         * <a href="#/users/{{ user._id }}" sd-with-params></a>
         * 
         */
        .directive('sdWithParams', ['locationParams', function(locationParams) {

            return {
                scope: true,
                compile: function(element, attrs, transclude) {
                    attrs.$set('href', attrs.href.trim() + locationParams.getQuery());
                }
            };
        }]);
});
