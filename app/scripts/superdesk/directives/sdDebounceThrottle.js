define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    var wrapper = function(methodName) {
        var interval = 1000;
        var func = _[methodName];

        return {
            require: ['ngModel'],
            link: function($scope, element, attrs, ctrl) {
                if (attrs.interval !== '') {
                    interval = attrs.interval;
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
    angular.module('superdesk.directives')
        .directive('sdDebounce', function() {
            return wrapper('debounce');
        })
        .directive('sdThrottle', function() {
            return wrapper('throttle');
        });
});
