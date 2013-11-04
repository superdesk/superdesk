define(function() {
    'use strict';

    return [function() {
        return {
            templateUrl: 'scripts/superdesk-users/views/edit-form.html',
            replace: true,
            scope: {
                user: '='
            }
        };
    }];
});
