
define(['angular'], function (angular) {
    'use strict';

    return angular.module('superdesk.avatar', [])
        .directive('sdUserAvatar', function() {
            return {
                scope: {src: '='},
                link: function (scope, element, attrs) {

                    element.on('error', function (e) {
                        element.hide();
                    });

                    scope.$watch('src', function (src) {
                        if (src) {
                            element.attr('src', src).show();
                        } else {
                            element.hide();
                        }
                    });
                }
            };

        });

});
