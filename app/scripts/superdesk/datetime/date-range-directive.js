define([], function() {
    'use strict';

	/**
     * Show date range picker on element
     *
     * Usage:
     * <input sd-date-range ng-model="mydate"></span>
     *
     * Params:
     * @scope {Object} ngModel
     *
     */
    return ['$location', function($location) {

        return {
            restrict: 'A',
            scope: {
                lte: '=',
                gte: '='
            },
			link: function(scope, elem, attributes) {

                // init
                var search = $location.search();
                scope.lte = search.before ? new Date(search.before) : null;
                scope.gte = search.after ? new Date(search.after) : null;

                scope.$watch('lte', function(lte) {
                    if (lte) {
                        var d = new Date(lte);
                        d.setHours(24, 0, 0, 0);
                        $location.search('before', d.toISOString());
                    } else {
                        $location.search('before', null);
                    }
                });

                scope.$watch('gte', function(gte) {
                    if (gte) {
                        var d = new Date(gte);
                        d.setHours(0, 0, 0, 0);
                        $location.search('after', d.toISOString());
                    } else {
                        $location.search('after', null);
                    }
                });
			}
        };
    }];
});
