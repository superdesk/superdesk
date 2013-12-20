define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.directives')
        .directive('sdConfirm', ['$window', function($window) {
            return {
                scope: {
                    msg: '@sdConfirm',
                    action: '&ngClick'
                },
                link: function(scope, element, attrs) {
                    element.click(function(e) {
                        if ($window.confirm(scope.msg)) {
                            scope.action();
                        }
                    });
                }
            };
        }]);
});