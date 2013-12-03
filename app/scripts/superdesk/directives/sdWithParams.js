define([
    'angular'
], function(angular) {
    'use strict';

    angular.module('superdesk.directives')
        /**
         * sdWithParams manipulates href attribute to include current parameters.
         *
         * Usage:
         * <a href="#/users/{{ user._id }}" sd-with-params data-exclude="id,date"></a>
         * 
         * Params:
         * @param {String} dataExclude - url parameters to exclude (separated by comma).
         */
        .directive('sdWithParams', ['locationParams', function(locationParams) {

            return {
                compile: function(element, attrs, transclude) {
                    if (attrs.exclude) {
                        var excludes = attrs.exclude.split(',');
                        attrs.$set('href', attrs.href.trim() + locationParams.makeQuery(_.omit(locationParams.params, excludes), locationParams.defaults));
                    } else {
                        attrs.$set('href', attrs.href.trim() + locationParams.getQuery());
                    }
                }
            };
        }]);
});
