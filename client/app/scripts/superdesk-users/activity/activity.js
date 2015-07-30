(function() {
    'use strict';

    angular.module('superdesk.users.activity', ['superdesk.users', 'superdesk.dashboard.widgets', 'superdesk.asset'])
        .config(['widgetsProvider', 'assetProvider', function(widgets, asset) {
            widgets.widget('activity', {
                label: 'Activity Stream',
                multiple: true,
                max_sizex: 2,
                max_sizey: 2,
                sizex: 1,
                sizey: 2,
                thumbnail: asset.imageUrl('superdesk-users/activity/thumbnail.svg'),
                template: asset.templateUrl('superdesk-users/activity/widget-activity.html'),
                configurationTemplate: asset.templateUrl('superdesk-users/activity/configuration.html'),
                configuration: {maxItems: 5},
                description: 'Activity stream widget',
                icon: 'stream'
            });
        }]).controller('ActivityController', ['$scope', 'profileService',
        function ($scope, profileService) {
            var page = 1;
            var current_config = null;
            $scope.max_results = 0;

            function refresh(config) {
                current_config = config;
                profileService.getUserActivityFiltered(config.maxItems).then(function(list) {
                    $scope.activityFeed = list;
                    $scope.max_results = parseInt(config.maxItems, 10);
                });

                $scope.loadMore = function() {
                    page++;
                    profileService.getUserActivityFiltered(config.maxItems, page).then(function(next) {
                        Array.prototype.push.apply($scope.activityFeed._items, next._items);
                        $scope.activityFeed._links = next._links;
                        $scope.max_results += parseInt(config.maxItems, 10);
                    });
                };
            }

            $scope.$on('changes in activity', function() {
                if (current_config) {
                    refresh(current_config);
                }
            });

            $scope.$watch('widget.configuration', function(config) {
                page = 1;
                if (config) {
                    refresh(config);
                }
            }, true);
        }]).controller('ActivityConfigController', ['$scope',
        function ($scope) {
            $scope.notIn = function(haystack) {
                return function(needle) {
                    return haystack.indexOf(needle) === -1;
                };
            };
        }]);
})();
