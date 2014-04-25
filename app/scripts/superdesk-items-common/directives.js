define(['angular', 'require'], function(angular, require) {
    'use strict';

    angular.module('superdesk.items-common.directives', [])
        .directive('sdMediaBox', ['$position', function($position) {
            return {
                restrict: 'A',
                templateUrl: require.toUrl('./views/media-box.html'),
                link: function(scope, element, attrs) {
                    scope.$watch('extras.view', function(view) {
                        switch (view) {
                        case 'mlist':
                        case 'compact':
                            scope.itemTemplate = require.toUrl('./views/media-box-list.html');
                            break;
                        default:
                            scope.itemTemplate = require.toUrl('./views/media-box-grid.html');
                        }
                    });
                }
            };
        }])
        .directive('sdMediaBoxHover', ['$position', function($position) {
            return {
                replace: true,
                templateUrl: require.toUrl('./views/media-box-hover.html')
            };
        }])
        .directive('sdSidebarLayout', ['$location', '$filter', function($location, $filter) {
            return {
                transclude: true,
                templateUrl: require.toUrl('./views/sidebar.html')
            };
        }])
        .directive('sdItemRendition', function() {
            return {
                templateUrl: require.toUrl('./views/item-rendition.html'),
                scope: {item: '=', rendition: '@'}
            };
        });
});
