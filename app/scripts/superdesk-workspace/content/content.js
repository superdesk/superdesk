(function() {
'use strict';

ContentCtrlFactory.$inject = ['api', 'superdesk'];
function ContentCtrlFactory(api, superdesk) {
    return function ContentCtrl($scope) {
        if ($scope) {
                $scope.highlight_configs = [];

                $scope.hasHighlights = function() {
                    return _.size($scope.highlight_configs) > 0;
                };

                $scope.$watch('selectedDesk', function(desk) {
                    if (desk) {
                        fetchHighlights(desk);
                    } else {
                        $scope.highlight_configs = [];
                    }
                });
        }

        function fetchHighlights(desk) {
                    api('highlights').query({where: {'desks': desk._id}})
                    .then(function(result) {
                        $scope.highlight_configs = result._items;
                    });
                }

        /**
         * Create an item and start editing it
         */
        this.create = function(type) {
            var item = {type: type || 'text'};
            api('archive')
                .save(item)
                .then(function() {
                    superdesk.intent('author', 'article', item);
                });
        };

        this.createPackage = function createPackage(current_item) {
            if (current_item) {
                superdesk.intent('create', 'package', {items: [current_item]});
            } else {
                superdesk.intent('create', 'package');
            }
        };
    };
}

angular.module('superdesk.workspace.content', [])
    .factory('ContentCtrl', ContentCtrlFactory);
})();
