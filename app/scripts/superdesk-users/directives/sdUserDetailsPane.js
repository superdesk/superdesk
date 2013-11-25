define([], function () {
    'use strict';

    return ['$timeout', function($timeout) {
        return {
            templateUrl: 'scripts/superdesk-users/views/user-details-pane.html',
            replace: true,
            scope: {
                user: '='
            },
            link: function(scope, element, attrs) {
                $timeout(function() {
                    $('.user-details-pane').addClass('open');
                });

                scope.closePane = function() {
                   $('.user-details-pane').removeClass('open');
                };
            }
        };
    }];
});