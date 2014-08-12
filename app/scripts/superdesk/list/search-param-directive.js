define([], function() {
    'use strict';

    return ['$location', function($location) {
        return {
            scope: {
                sdSearchParam: '@',
                empty: '&'
            },
            link: function(scope, elem) {
                var params = $location.search();
                elem.val(params[scope.sdSearchParam]);

                var updateParam = _.debounce(function() {
                    scope.$apply(function() {
                        $location.search('q', elem.val() || null);
                        $location.search('page', null);
                    });
                }, 500);

                scope.$on('$routeUpdate', function() {
                    params = $location.search();
                    var val = params[scope.sdSearchParam];
                    if (val !== elem.val()) {
                        elem.val(val || '');
                        updateParam();
                    }
                 });

                elem.keyup(updateParam);
            }
        };
    }];
});
