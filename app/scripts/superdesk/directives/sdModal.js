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
        });
});
