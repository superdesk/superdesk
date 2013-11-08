define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'items', 'em', 'notify', 'gettext',
    function($scope, items, em, notify, gettext) {

        $scope.items = items;

        $scope.archive = function(item) {
            notify.info(gettext('Saving..'));
            em.create('archive', item).then(function() {
                notify.pop();
                notify.success(gettext('Item archived!'), 3000);
            });
        };
    }];
});
