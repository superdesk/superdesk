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
                scope.lte = search.before || null;
                scope.gte = search.after || null;

                // change location on change
                scope.$watch('lte + gte', function() {
                    console.log(scope.lte, scope.gte);
                    $location.search('before', scope.lte || null);
                    $location.search('after', scope.gte || null);
                });
			}
        };
    }];
});
