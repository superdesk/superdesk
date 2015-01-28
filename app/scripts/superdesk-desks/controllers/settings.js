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

            function getExpiryHours(inputMin) {
                return Math.floor(inputMin / 60);
            }
            function getExpiryMinutes(inputMin) {
                return Math.floor(inputMin % 60);
            }
            $scope.getTotalExpiryMinutes = function(contentExpiry) {
                return (contentExpiry.Hours * 60) + contentExpiry.Minutes;
            };

            $scope.setContentExpiryHoursMins = function(container) {
                var objContentExpiry = {
                    Hours: 0,
                    Minutes: 0
                };
                if (container.content_expiry != null) {
                    objContentExpiry.Hours = getExpiryHours(container.content_expiry);
                    objContentExpiry.Minutes = getExpiryMinutes(container.content_expiry);
                }
                return objContentExpiry;
            };

            $scope.setSpikeExpiryHoursMins = function(container) {
                var objSpikeExpiry = {
                    Hours: 0,
                    Minutes: 0
                };

                if (container.spike_expiry != null) {
                    objSpikeExpiry.Hours = getExpiryHours(container.spike_expiry);
                    objSpikeExpiry.Minutes = getExpiryMinutes(container.spike_expiry);
                }
                return objSpikeExpiry;
            };

        }];
});
