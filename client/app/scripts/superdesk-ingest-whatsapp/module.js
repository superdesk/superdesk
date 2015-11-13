define([
    'angular',
    'd3',
    'moment',
], function(angular, d3, moment) {
    'use strict';

    var modulePath = 'scripts/superdesk-ingest-whatsapp';

    var app = angular.module('superdesk.ingest.whatsapp', [
        'superdesk.ingest'
    ]);

    app.run(['providerTypes', function(providerTypes) {
        providerTypes.whatsapp = {
            label: 'WhatsApp',
            templateUrl: modulePath + '/views/whatsappConfig.html'
        };
    }]);

    app.directive('sdWhatsappRegistration', ['api', 'notify', 'gettext',
    function(api, notify, gettext) {
        return {
            scope: {
                provider: '='
            },
            templateUrl: modulePath + '/views/whatsappRegistration.html',
            link: function($scope) {
                $scope.activation = {};
                $scope.code_request_sent = false;
                $scope.registration_request_sent = false;

                $scope.sendActivation = function() {
                    if (
                        !$scope.provider.config.phone ||
                        !$scope.activation.cc ||
                        !$scope.activation.mcc ||
                        !$scope.activation.mnc
                    ) {
                        notify.error(gettext('Please fill phone, CC, MCC and MNC fields.'));
                        return;
                    }
                    api.save('whatsapp_code_request', {
                        'phone': $scope.provider.config.phone,
                        'cc': $scope.activation.cc,
                        'mcc': $scope.activation.mcc,
                        'mnc': $scope.activation.mnc
                    }).then(function(result) {
                        $scope.code_request_id = result._id;
                    });
                };
                $scope.$on('whatsapp_code_request', function(_e, data) {
                    if (data.id !== $scope.code_request_id) { return; }
                    if (data.result.status === 'sent') {
                        $scope.code_request_sent = true;
                        $scope.$apply(function() {
                            notify.success(gettext('Activation code was sent to your phone.'));
                        });
                    } else {
                        console.log(data.result);
                        $scope.$apply(function() {
                            notify.error(data.result);
                        });
                    }
                    $scope.code_request_id = null;
                });

                $scope.getPassword = function() {
                    if (
                        !$scope.provider.config.phone ||
                        !$scope.activation.cc ||
                        !$scope.activation.code
                    ) {
                        notify.error(gettext('Please fill phone, CC and activation code fields.'));
                        return;
                    }
                    api.save('whatsapp_registration_request', {
                        'phone': $scope.provider.config.phone,
                        'cc': $scope.activation.cc,
                        'code': $scope.activation.code
                    }).then(function(result) {
                        $scope.registration_request_id = result._id;
                    });
                };
                $scope.$on('whatsapp_registration_request', function(_e, data) {
                    if (data.id !== $scope.registration_request_id) { return; }
                    if (data.result.pw) {
                        $scope.provider.config.password = data.result.pw;
                        $scope.registration_request_sent = true;
                        $scope.$apply(function() {
                            notify.success(gettext('Password field was filled in.'));
                        });
                    } else {
                        console.log(data.result);
                        $scope.$apply(function() {
                            notify.error(data.result);
                        });
                    }
                    $scope.registration_request_id = null;
                });
            }
        };
    }]);

    return app;

});
