
define(['angular'], function (angular) {
    'use strict';

    return angular.module('superdesk.avatar', [])
        .directive('sdUserAvatar', function() {
            return {
                scope: {src: '='},
                link: function (scope, element, attrs) {

                    var figure = element.parents('figure');

                    element.on('error', function (e) {
                        element.hide();
                    });

                    scope.$watch('src', function (src) {
                        if (src) {
                            element.attr('src', src).show();
                            figure.addClass('no-bg');
                        } else {
                            element.hide();
                            figure.removeClass('no-bg');
                        }
                    });
                }
            };

        });

});
