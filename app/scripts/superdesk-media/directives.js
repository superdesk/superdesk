define([
    'lodash',
    'jquery',
    'angular'
], function(_, $, angular) {
    'use strict';

    angular.module('superdesk.media.directives', [])

        .directive('sdInlineMeta', function() {
            return {
                templateUrl: 'scripts/superdesk-media/views/sd-inline-meta.html',
                scope: {
                    'placeholder': '@',
                    'showmeta': '=',
                    'item': '=',
                    'setmeta': '&'
                }
            };
        });
});
