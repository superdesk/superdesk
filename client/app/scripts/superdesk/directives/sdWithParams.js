define([
    'angular'
], function(angular) {
    'use strict';

    return angular.module('superdesk.links', [])
        /**
         * sdWithParams manipulates href attribute to include current parameters.
         *
         * Usage:
         * <a href="#/users/{{ user._id }}" sd-with-params data-exclude="id,date"></a>
         *
         * Params:
         * @attr {String} exclude - url parameters to exclude (separated by comma).
         */
        .directive('sdWithParams', ['locationParams', function(locationParams) {

            return {
                compile: function(element, attrs, transclude) {
                    if (attrs.exclude) {
                        var excludes = attrs.exclude.split(',');
                        var query = locationParams.makeQuery(_.omit(locationParams.params, excludes), locationParams.defaults);
                        attrs.$set('href', attrs.href.trim() + query);
                    } else {
                        attrs.$set('href', attrs.href.trim() + locationParams.getQuery());
                    }
                }
            };
        }]);
});
