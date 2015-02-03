define(['angular'], function(angular) {
    'use strict';

    return angular.module('superdesk.search.dir', [])
    /**
     * Search directive wraps locationParams for search
     *
     * Usage:
     * <div sd-search="username"><input type="text" ng-model="q" ng-change="search(q)" /></div>
     */
    .directive('sdSearch', function(locationParams) {
        return {
            priority: 10,
            link: function(scope, element, attrs) {
                var query = locationParams.get('search') || '';
                var qParts = query.split(':');
                if (qParts[0] === attrs.sdSearch) {
                    element.find('input').val(qParts[qParts.length - 1]);
                } else {
                    element.find('input').val(locationParams.get('search'));
                }

                scope.search = function(q) {
                    var split = q.split(':');
                    if (split.length === 2) {
                        locationParams.set('search', q);
                    } else if (q) {
                        locationParams.set('search', attrs.sdSearch + ':' + q);
                    } else {
                        locationParams.set('search', null);
                    }
                };
            }
        };
    });
});
