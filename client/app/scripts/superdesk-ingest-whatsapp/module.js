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
                $scope.sendActivation = function() {
                    notify.success(gettext('Activation code was sent to your phone.'));
                };
                $scope.getPassword = function() {
                    notify.success(gettext('Password field was filled in.'));
                };
                console.log('whatsappregistration');
            }
        };
    }]);

    return app;

});
