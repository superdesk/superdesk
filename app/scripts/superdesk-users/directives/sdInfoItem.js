define(function () {
    'use strict';

    return function () {
        return {
            link: function (scope, element) {
                element.addClass('info-item');
                element.find('label').addClass('info-label');
                element.find('input').addClass('info-value');
                element.find('input').addClass('info-editable');
            }
        };
    };
});