define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    return angular.module('superdesk.directives.modal', [])
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
                template: '<div class="modal fade">' +
                        '<div class="modal-dialog" ng-if="model"><div class="modal-content" ng-transclude></div></div>' +
                    '</div>',
                scope: {model: '='},
                link: function(scope, element, attrs) {
                    scope.$watch('model', function(model) {
                        $(element).modal(model ? 'show' : 'hide');
                    });
                }
            };
        });
});
