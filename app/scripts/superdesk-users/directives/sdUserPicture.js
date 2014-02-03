define([], function () {
    'use strict';

    return [function() {
        function getDefaultPicture() {
            return 'images/avatar_default.png';
        }

        return {
            scope: {src: '='},
            link: function (scope, element, attrs) {
                scope.$watch('src', function (src) {
                    element.on('error', function (e) {
                        element.attr('title', gettext('Error when loading: ') + element.attr('src'));
                        element.attr('src', getDefaultPicture());
                    });

                    element.attr('src', src ? src : getDefaultPicture());
                });
            }
        };
    }];
});
