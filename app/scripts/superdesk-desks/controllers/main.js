define(['lodash'], function(_) {
    'use strict';

    DeskListController.$inject = ['$scope', 'api'];
    function DeskListController($scope, api) {

        api.desks.query()
            .then(function(desks) {
                $scope.desks = desks;
            });
    }

    return DeskListController;

});
