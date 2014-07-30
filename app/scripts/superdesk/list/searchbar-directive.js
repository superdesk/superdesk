define(['require'], function(require) {
    'use strict';

    return ['$location', function($location) {
        return {
            scope: true,
            replace: true,
            templateUrl: require.toUrl('./views/searchbar.html'),
            link: function(scope, element) {
                var search = $location.search();
                scope.flags = {open: !!search.q};
            }
        };
    }];
});
