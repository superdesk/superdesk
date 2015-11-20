
define(['angular'], function (angular) {
    'use strict';

    return angular.module('superdesk.avatar', [])
        .directive('sdUserAvatar', function() {
            return {
                scope: {user: '='},
                link: function (scope, element, attrs) {
                    scope.$watch('user', function (user) {
                        if (user) {
                            initAvatar(user);
                        }
                    });

                    element.on('error', function (e) {
                        element.hide();
                    });

                    function initAvatar(user) {
                        var figure = element.parents('figure');

                        if (user.picture_url) {
                            element.attr('src', user.picture_url).show();
                            figure.addClass('no-bg');

                        } else if (user.display_name) {
                            var initials = user.display_name.replace(/\W*(\w)\w*/g, '$1').toUpperCase();

                            element.hide();
                            figure.addClass('initials');

                            if (figure.has('> span').length) {
                                figure.children('span').text(initials);
                            } else {
                                figure.prepend('<span>' + initials + '</span>');
                            }

                        } else {
                            element.hide();
                            figure.removeClass('no-bg');
                        }
                    }
                }
            };

        });

});
