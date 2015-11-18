define(['angular'], function(angular) {
    'use strict';

    var render = function(element, value) {
        element.toggleClass('checked', !!value);
        element.attr('checked', !!value);
    };

    return angular.module('superdesk.check.directives', [])
        /**
         * sdCheck creates a custom-styled checkbox.
         *
         * Usage:
         * <input sd-check ng-model="user._checked">
         *
         * Params:
         * @scope {boolean} ngModel - model for checkbox value
         */
        .directive('sdCheck', function() {
            return {
                require: 'ngModel',
                replace: true,
                template: '<span class="sd-checkbox"></span>',
                link: function($scope, element, attrs, ngModel) {
                    ngModel.$render = function() {
                        render(element, ngModel.$viewValue);
                    };

                    $scope.$watch(attrs.ngModel, function() {
                        render(element, ngModel.$viewValue);
                    });

                    element.on('click', function(e) {
                        $scope.$apply(function() {
                            ngModel.$setViewValue(!ngModel.$viewValue);
                        });

                        return false;
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
         * @scope {array} ngModel - array of objects managed by checkboxes
         * @scope {string} checkAttribute - name of attribute to set in model elements
         *
         */
        .directive('sdCheckAll', function() {
            var checkAttribute = '_checked';

            return {
                require: 'ngModel',
                replace: true,
                template: '<span class="sd-checkbox"></span>',
                link: function($scope, element, attrs, ngModel) {
                    var checked = false;
                    if (attrs.checkAttribute !== undefined) {
                        checkAttribute = attrs.checkAttribute;
                    }

                    $scope.$watch(attrs.ngModel, function(model) {
                        if (model) {
                            checked = (_.every(ngModel.$viewValue, checkAttribute) && (ngModel.$viewValue.length > 0));
                            render(element, checked);
                        }
                    }, true);

                    element.on('click', function() {
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
        })

/**
         * Inverted - sdSwitchInverted is sdCheck directive with inverted functionality
         * e.g: useful in case when we want to display switch ON (means provider is open) for model like provider.is_closed = false
         * and vice versa.
         * Usage:
         * <input sd-switch-inverted ng-model="provider.is_closed">
         *
         * Params:
         * @scope {boolean} ngModel - model for checkbox value
         */
        .directive('sdSwitchInverted', function() {
            return {
                require: 'ngModel',
                replace: true,
                template: [
                    '<span class="sd-toggle">',
                    '<span class="inner"></span>',
                    '</span>'
                ].join(''),
                link: function($scope, element, attrs, ngModel) {
                    ngModel.$render = function() {
                        render(element, ngModel.$viewValue);
                    };

                    $scope.$watch(attrs.ngModel, function() {
                        render(element, !ngModel.$viewValue);
                    });

                    element.on('click', function(e) {
                        $scope.$apply(function() {
                            ngModel.$setViewValue(!ngModel.$viewValue);
                        });

                        return false;
                    });
                }
            };
        })

        /**
         * sdSwitch is sdCheck directive with different styling
         *
         * Usage:
         * <input sd-switch ng-model="notifications.show">
         *
         * Params:
         * @scope {boolean} ngModel - model for checkbox value
         */
        .directive('sdSwitch', function() {
            return {
                require: 'ngModel',
                replace: true,
                template: [
                    '<span class="sd-toggle">',
                    '<span class="inner"></span>',
                    '</span>'
                ].join(''),
                link: function($scope, element, attrs, ngModel) {
                    ngModel.$render = function() {
                        render(element, ngModel.$viewValue);
                    };

                    $scope.$watch(attrs.ngModel, function() {
                        render(element, ngModel.$viewValue);
                    });

                    element.on('click', function(e) {
                        $scope.$apply(function() {
                            ngModel.$setViewValue(!ngModel.$viewValue);
                        });

                        return false;
                    });
                }
            };
        });

});
