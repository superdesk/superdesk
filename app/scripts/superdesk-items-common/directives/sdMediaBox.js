define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    angular.module('superdesk.items-common.directives')
        .directive('sdMediaBox', ['$position', function($position) {
            return {
                restrict: 'A',
                templateUrl: 'scripts/superdesk-items-common/views/media-box.html',
                link: function(scope, element, attrs) {
                    scope.$watch('extras.view', function(view) {
                        switch (view) {
                        case 'mlist':
                        case 'compact':
                            scope.itemTemplate = 'scripts/superdesk-items-common/views/media-box-list.html';
                            break;
                        default:
                            scope.itemTemplate = 'scripts/superdesk-items-common/views/media-box-grid.html';
                        }
                    });
                }
            };
        }])
        .directive('sdMediaBoxHover', ['$position', function($position) {
            return {
                restrict: 'A',
                templateUrl: 'scripts/superdesk-items-common/views/media-box-hover.html',
                replace: true,
                link: function(scope, element, attrs) {
                }
            };
        }]);
});
