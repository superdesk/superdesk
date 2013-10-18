define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    var wrapper = function(methodName, paramName) {
        var func = _[methodName];
        return {
            scope: {
                bounce: '&' + paramName,
                value: '@'
            },
            link: function(scope, element, attrs, ngModel) {
                var interval = attrs.interval || 1000;
                element.off('input').off('keydown').off('change');
                element.on('input', func(function() {
                    scope.$apply(function() {
                        scope.bounce({val: element.val()});
                    });
                }, interval));
            }
        };
    };

    
    angular.module('superdesk.directives')
        /**
         * sdDebounce debounces model update.
         *
         * Usage:
         * <input sd-debounce data-interval="1500" ng-model="keyword">
         *
         * Params:
         * @param {number} interval
         * @param {object} ngModel
         */
        .directive('sdDebounce', function() {
            return wrapper('debounce', 'sdDebounce');
        })

        /**
         * sdThrottle throttles model update.
         *
         * Usage:
         * <input sd-throttle data-interval="1500" ng-model="keyword">
         *
         * Params:
         * @param {number} interval
         * @param {object} ngModel
         */
        .directive('sdThrottle', function() {
            return wrapper('throttle', 'sdThrottle');
        });
});
