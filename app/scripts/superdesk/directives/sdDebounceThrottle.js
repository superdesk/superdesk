define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    var wrapper = function(method) {
        var interval = 1000;
        var attribute = 'sd' + method.charAt(0).toUpperCase() + method.slice(1);
        var func = _[method];

        return {
            require: ['ngModel'],
            link: function($scope, element, attrs, ctrl) {
                if (attrs[attribute] !== '') {
                    interval = attrs[attribute];
                }
                element.unbind('input').unbind('keydown').unbind('change');
                element.bind('input', func(function() {
                    $scope.$apply(function() {
                        ctrl[0].$setViewValue(element.val());
                    });
                }, interval));
            }
        };
    };

    angular.module('superdesk.directives')
        .directive('sdDebounce', function() {
            return wrapper('debounce');
        })
        .directive('sdThrottle', function() {
            return wrapper('throttle');
        });
});
