define([
    'jquery',
    'angular',
    'bootstrap/modal',
    'bootstrap_ui'
], function($, angular) {
    'use strict';

    angular.module('superdesk.directives')
        .directive('sdModal', function() {
            return {
                link: function(scope, element, attrs) {
                    var show = false;
                    if ('ngShow' in attrs) {
                        show = !!scope.$eval(attrs.ngShow);
                    }

                    $(element).addClass('modal fade');
                    $(element).modal({
                        show: show
                    });
                }
            };
        })
        /**
         * Modal View directive
         *
         * Provides wrapper for modal views.
         *
         * @param {Object} data-model - if true modal is open, otherwise it's closed
         */
        .directive('sdModalView', function() {
            return {
                replace: true,
                transclude: true,
                template: '<div class="modal fade"><div class="modal-dialog"><div class="modal-content" ng-transclude></div></div></div>',
                scope: {
                    model: '='
                },
                link: function(scope, element, attrs) {
                    $(element).modal({show: !!scope.model});
                    scope.$watch('model', function(model) {
                        $(element).modal(model ? 'show' : 'hide');
                    });
                }
            };
        });
});
