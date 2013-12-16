
define(['angular'], function (angular) {
    'use strict';
    
    angular.module('superdesk.directives')
        .directive('sdUserAvatar', function() {
            return {
                scope: {src: '='},
                link: function (scope, element, attrs) {
                    
                    function getDefaultPicture() {
                        return 'images/avatar_default.png';
                    }

                    scope.$watch('src', function (src) {
                        element.on('error', function (e) {
                            element.attr('title', gettext('Error when loading: ') + element.attr('src'));
                            element.attr('src', getDefaultPicture());
                        });

                        element.attr('src', src ? src : getDefaultPicture());
                    });
                }
            };

        });

});
