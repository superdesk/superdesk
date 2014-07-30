define(['moment'], function(moment) {
    'use strict';

    function format(date) {
        return date ? moment(date).format('YYYY-MM-DD') : null;
    }

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
                    $location.search('before', format(lte));
                });

                scope.$watch('gte', function(gte) {
                    $location.search('after', format(gte));
                });
			}
        };
    }];
});
