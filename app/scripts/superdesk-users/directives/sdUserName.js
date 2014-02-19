define(function () {
    'use strict';

    return ['em', function (em) {
        return {
            require: 'ngModel',
            link: function (scope, element, attrs, ctrl) {
                ctrl.$parsers.unshift(function(viewValue) {
                    if (viewValue) {
                        em.getRepository('users').matching({where: {username: viewValue}}).then(function(result) {
                            ctrl.$setValidity('usernameavailable', result._items.length === 0);
                        });
                    }
                });
            }
        };
    }];
});
