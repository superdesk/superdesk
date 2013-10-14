define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    var render = function(element, value) {
        element.toggleClass('sf-checked', !!value);
        element.attr('checked', !!value);
    };

    angular.module('superdesk.directives')
        /**
         * sdCheck creates a custom-styled checkbox.
         *
         * Usage:
         * <input sd-check ng-model="user._checked">
         * 
         * Params:
         * @param {boolean} ngModel - model for checkbox value
         *
         */
        .directive('sdCheck', function() {
            return {
                require: 'ngModel',
                replace: true,
                template: '<span class="sf-checkbox-custom"></span>',
                link: function($scope, element, attrs, ngModel) {
                    ngModel.$render = function() {
                        render(element, ngModel.$viewValue);
                    };

                    $scope.$watch(attrs.ngModel, function() {
                        render(element, ngModel.$viewValue);
                    });

                    element.on('click', function(){
                        $scope.$apply(function() {
                            ngModel.$setViewValue(!ngModel.$viewValue);
                        });
                    });
                }
            };
        })
        /**
         * sdCheckAll creates a custom-styled checkbox managing other checkboxes in the same group.
         *
         * Usage:
         * <input sd-check-all ng-model="users" data-check-attribute="_checked">
         * 
         * Params:
         * @param {array} ngModel - array of objects managed by checkboxes
         * @param {string} checkAttribute - name of attribute to set in model elements
         *
         */
        .directive('sdCheckAll', function() {
            var checkAttribute = '_checked';

            return {
                require: 'ngModel',
                replace: true,
                template: '<span class="sf-checkbox-custom"></span>',
                link: function($scope, element, attrs, ngModel) {
                    var checked = false;
                    if (attrs.checkAttribute !== undefined) {
                        checkAttribute = attrs.checkAttribute;
                    }

                    $scope.$watch(attrs.ngModel, function() {
                        checked = _.every(ngModel.$viewValue, checkAttribute);
                        render(element, checked);
                    }, true);

                    element.on('click', function(){
                        checked = !checked;
                        
                        var model = ngModel.$viewValue;
                        _.forEach(model, function(item) {
                            item[checkAttribute] = checked;
                        });
                        $scope.$apply(function() {
                            ngModel.$setViewValue(model);
                        });

                        render(element, checked);
                    });
                }
            };
        });
});
