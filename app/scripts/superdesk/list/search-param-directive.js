define([], function() {
    'use strict';

    return ['$location', function($location) {
        return {
            scope: {
                sdSearchParam: '@'
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

                elem.keyup(updateParam);
            }
        };
    }];
});
