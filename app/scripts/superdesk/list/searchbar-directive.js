define(['require'], function(require) {
    'use strict';

    return ['$location', function($location) {
        return {
            scope: true,
            templateUrl: require.toUrl('./views/searchbar.html'),
            link: function(scope, elem) {
                var input = elem.find('#search-input');
                var params = $location.search();
                scope.search = params.q;
                scope.flags = {extended: !!scope.search};

                var updateParam = _.debounce(function() {
                    scope.$apply(function() {
                        $location.search('q', scope.search || null);
                        $location.search('page', null);
                    });
                }, 500);

                scope.$watch('search', function() {
                    updateParam();
                });

                scope.close = function() {
                    scope.search = null;
                    input.focus();
                };

            }
        };
    }];
});
