
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
                    }, true);

                    var figure = element.parents('figure');

                    element.on('error', function (e) {
                        showInitials(scope.user.display_name);
                    });

                    function initAvatar(user) {
                        if (user.picture_url) {
                            showPicture(user.picture_url);
                        } else if (user.display_name) {
                            showInitials(user.display_name);
                        } else {
                            element.hide();
                            figure.children('span').hide();
                            figure.removeClass('no-bg initials');
                        }
                    }

                    function showPicture(url) {
                        figure.children('span').hide();
                        figure.addClass('no-bg');
                        figure.removeClass('initials');

                        element.attr('src', url).show();
                    }

                    function showInitials(name) {
                        var initials = name.replace(/\W*(\w)\w*/g, '$1').toUpperCase();

                        element.hide();
                        figure.addClass('initials');
                        figure.removeClass('no-bg');

                        if (figure.has('> span').length) {
                            figure.children('span').text(initials).show();
                        } else {
                            figure.prepend('<span>' + initials + '</span>');
                        }
                    }
                }
            };

        });

});
