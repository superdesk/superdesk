define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    return ['$scope', 'gettext', 'notify', 'api', 'desks', 'WizardHandler',
        function($scope, gettext, notify, api, desks, WizardHandler) {
            $scope.modalActive = false;
            $scope.step = {
                current: null
            };
            $scope.desk = {
                edit: null
            };
            $scope.desks = {};

            desks.initialize()
            .then(function() {
                $scope.desks = desks.desks;
            });

            $scope.openDesk = function(step, desk) {
                $scope.desk.edit = desk;
                $scope.modalActive = true;
                $scope.step.current = step;
            };

            $scope.cancel = function() {
                $scope.modalActive = false;
                $scope.step.current = null;
                $scope.desk.edit = null;
            };

            $scope.remove = function(desk) {
                api.desks.remove(desk).then(function() {
                    _.remove($scope.desks._items, desk);
                    notify.success(gettext('Desk deleted.'), 3000);
                });
            };

            $scope.getExpiryHours = function(inputMin) {
                return parseInt(inputMin / 60, 10);
            };
            $scope.getExpiryMinutes = function(inputMin) {
                return parseInt(inputMin % 60, 10);
            };
            $scope.getTotalExpiryMinutes = function(contentExpiry) {
                return (contentExpiry.Hours * 60) + contentExpiry.Minutes;
            };

            $scope.setContentExpiryHoursMins = function(container) {
                var objContentExpiry = {
                    Hours: 0,
                    Minutes: 0
                };
                if (typeof (container.content_expiry) !== 'undefined' && (container.content_expiry) !== null) {
                    objContentExpiry.Hours = $scope.getExpiryHours(container.content_expiry);
                    objContentExpiry.Minutes = $scope.getExpiryMinutes(container.content_expiry);
                }
                return objContentExpiry;
            };

            $scope.setSpikeExpiryHoursMins = function(container) {
                var objSpikeExpiry = {
                    Hours: 0,
                    Minutes: 0
                };

                if (typeof (container.content_expiry) !== 'undefined' && (container.spike_expiry) !== null) {
                    objSpikeExpiry.Hours = $scope.getExpiryHours(container.spike_expiry);
                    objSpikeExpiry.Minutes = $scope.getExpiryMinutes(container.spike_expiry);
                }
                return objSpikeExpiry;
            };

        }];
});
