define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    var wrapper = function(methodName) {
        var interval = 1000;
        var func = _[methodName];

        return {
            require: 'ngModel',
            link: function($scope, element, attrs, ngModel) {
                if (attrs.interval !== '' && attrs.interval !== undefined) {
                    interval = attrs.interval;
                }
                element.off('input').off('keydown').off('change');
                element.on('input', func(function() {
                    $scope.$apply(function() {
                        ngModel.$setViewValue(element.val());
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
            return wrapper('debounce');
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
            return wrapper('throttle');
        });
});