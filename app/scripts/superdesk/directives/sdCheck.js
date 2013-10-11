define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    var render = function(element, value) {
        element.toggleClass('sf-checked', value);
        element.attr('checked', value);
    };

    angular.module('superdesk.directives')
        /**
         * sdCheck creates a custom-styled checkbox.
         *
         * Usage:
         * <input sd-check ng-model="check" data-check-group="users">
         * 
         * Params:
         * @param {boolean} ngModel - model for checkbox value
         * @param {string} checkGroup - group name to be used in "select all"
         *
         */
        .directive('sdCheck', function($timeout) {
            return {
                require: 'ngModel',
                replace: true,
                template: '<span class="sf-checkbox-custom"></span>',
                link: function($scope, element, attrs, ngModel) {
                    $timeout(function() {
                        render(element, ngModel.$viewValue);
                    });

                    element.on('click', function(){
                        $scope.$apply(function() {
                            ngModel.$setViewValue(!ngModel.$viewValue);
                            render(element, ngModel.$viewValue);
                        });
                    });
                }
            };
        })
        /**
         * sdCheckAll creates a custom-styled checkbox managing other checkboxes in the same group.
         *
         * Usage:
         * <input sd-check-all data-check-group="users">
         * 
         * Params:
         * @param {string} checkGroup - group name to manage
         *
         */
        .directive('sdCheckAll', function($timeout) {
            return {
                replace: true,
                template: '<span class="sf-checkbox-custom"></span>',
                link: function($scope, element, attrs) {
                    var checked = false;
                    var elements = $('[data-check-group="' + attrs.checkGroup + '"]:not([sd-check-all])');

                    var process = function() {
                        var numChecked = 0;
                        for (var i = 0; i < elements.length; i++) {
                            var el = elements[i];
                            if (el.getAttribute('checked') !== null) {
                                numChecked = numChecked + 1;
                            }
                        }
                        if (numChecked === elements.length) {
                            checked = true;
                        } else {
                            checked = false;
                        }
                    };
                    
                    elements.on('click', function() {
                        $timeout(function() {
                            process();
                            render(element, checked);
                        });
                    });

                    element.on('click', function() {
                        checked = !checked;
                        render(element, checked);
                        for (var i = 0; i < elements.length; i++) {
                            var el = elements[i];
                            if ((checked === true && el.getAttribute('checked') === null)
                             || (checked === false && el.getAttribute('checked') !== null)) {
                                el.click();
                            }
                        }
                    });
                }
            };
        });
});
