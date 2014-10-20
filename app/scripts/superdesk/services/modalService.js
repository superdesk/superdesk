define(['angular'], function(angular) {
    'use strict';

    return angular.module('superdesk.services.modal', ['ui.bootstrap'])
        .service('modal', ['$q', '$modal', function($q, $modal) {
            this.confirm = function(bodyText, headerText, okText, cancelText) {
                headerText = headerText || gettext('Confirm');
                okText = okText || gettext('OK');
                cancelText = cancelText || gettext('Cancel');

                var delay = $q.defer();

                $modal.open({
                    templateUrl: 'scripts/superdesk/views/confirmation-modal.html',
                    controller: ['$scope', '$modalInstance', function($scope, $modalInstance) {
                        $scope.headerText = headerText;
                        $scope.bodyText = bodyText;
                        $scope.okText = okText;
                        $scope.cancelText = cancelText;

                        $scope.ok = function() {
                            delay.resolve(true);
                            $modalInstance.close();
                        };

                        $scope.cancel = function() {
                            delay.reject();
                            $modalInstance.dismiss();
                        };
                    }]
                });

                return delay.promise;
            };

        }]);
});
