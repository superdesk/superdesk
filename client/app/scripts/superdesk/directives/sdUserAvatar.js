
define(['angular'], function (angular) {
    'use strict';

    return angular.module('superdesk.avatar', [])
        .directive('sdUserAvatar', function() {
            return {
                scope: {src: '=', initials: '='},
                link: function (scope, element, attrs) {

                    var figure = element.parents('figure');

                    element.on('error', function (e) {
                        element.hide();
                    });

                    scope.$watch('src', initAvatar);
                    scope.$watch('initials', initAvatar);

                    function initAvatar() {
                        if (scope.src) {
                            element.attr('src', scope.src).show();
                            figure.addClass('no-bg');
                        } else if (scope.initials) {
                            var initials = scope.initials.replace(/\W*(\w)\w*/g, '$1').toUpperCase();
                            element.hide().parent().html(initials);
                            figure.addClass('initials');
                        } else {
                            element.hide();
                            figure.removeClass('no-bg');
                        }
                    }
                }
            };

        });

});
