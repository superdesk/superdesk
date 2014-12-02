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
                gte: '=',
                field: '='},
			link: function(scope, elem, attributes) {

                // init
                var search = $location.search();
                if (attributes.field === 'firstcreated')
                {
                    scope.lte = search.beforefirstcreated ? new Date(search.beforefirstcreated) : null;
                    scope.gte = search.afterfirstcreated ? new Date(search.afterfirstcreated) : null;
                }
                if (attributes.field === 'versioncreated')
                {
                    scope.lte = search.beforeversioncreated ? new Date(search.beforeversioncreated) : null;
                    scope.gte = search.afterversioncreated ? new Date(search.afterversioncreated) : null;
                }
                scope.field = attributes.field;

                scope.$watch('lte', function(lte) {
                    if (lte) {
                        var d = new Date(lte);
                        d.setHours(24, 0, 0, 0);
                        $location.search('before' + scope.field, d.toISOString());
                    } else {
                        $location.search('before' + scope.field, null);
                    }
                });

                scope.$watch('gte', function(gte) {
                    if (gte) {
                        var d = new Date(gte);
                        d.setHours(0, 0, 0, 0);
                        $location.search('after' + scope.field, d.toISOString());
                    } else {
                        $location.search('after' + scope.field, null);
                    }
                });
			}
        };
    }];
});
