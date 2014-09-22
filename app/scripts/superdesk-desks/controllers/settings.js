define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    return ['$scope', 'gettext', 'notify', 'api', 'desks',
        function($scope, gettext, notify, api, desks) {

            $scope.currentStep = null;
            $scope.modalActive = false;
            $scope.desk = {
                edit: null
            };
            $scope.desks = {};

            desks.fetchDesks()
            .then(function() {
                $scope.desks = desks.desks;
            });

            $scope.openDesk = function(step, desk) {
                $scope.desk.edit = desk;
                $scope.currentStep = step;
                $scope.modalActive = true;
            };

            $scope.cancel = function() {
                $scope.modalActive = false;
                $scope.desk.edit = null;
            };

			$scope.remove = function(desk) {
                api.desks.remove(desk).then(function() {
                    _.remove($scope.desks._items, desk);
                    notify.success(gettext('Desk deleted.'), 3000);
                });
            };

		}];
});
