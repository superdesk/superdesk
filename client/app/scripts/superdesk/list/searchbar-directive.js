define(['require'], function(require) {
    'use strict';

    return ['$location', function($location) {
        return {
            scope: true,
            templateUrl: require.toUrl('./views/searchbar.html'),
            link: function(scope, elem) {
                var input = elem.find('#search-input');
                scope.q = $location.search().q || null;
                scope.flags = {extended: !!scope.q};

                scope.search = function() {
                    $location.search('q', scope.q || null);
                    $location.search('page', null);
                };

                scope.close = function() {
                    scope.q = null;
                    input.focus();
                };
            }
        };
    }];
});
