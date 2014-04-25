define([
    'lodash',
    'angular',
    'require',
    './media-view-directive'
], function(_, angular, require) {
    'use strict';

    return angular.module('superdesk.media.directives', [])
        .directive('sdInlineMeta', function() {
            return {
                templateUrl: require.toUrl('./views/sd-inline-meta.html'),
                scope: {
                    'placeholder': '@',
                    'showmeta': '=',
                    'item': '=',
                    'setmeta': '&'
                }
            };
        })
        .directive('sdMediaPreview', [function() {
            return {
                replace: true,
                templateUrl: require.toUrl('./views/preview.html'),
                scope: {item: '='}
            };
        }])
        .directive('sdMediaView', require('./media-view-directive'));
});
