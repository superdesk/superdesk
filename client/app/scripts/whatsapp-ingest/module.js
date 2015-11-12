define([
    'angular',
    'd3',
    'moment',
], function(angular, d3, moment) {
    'use strict';

    var app = angular.module('superdesk.ingest.whatsapp', [
        'superdesk.ingest'
    ]);

    app.run(['providerTypes', function(providerTypes) {
        providerTypes.whatsApp = {
            label: 'WhatsApp',
            templateUrl: 'scripts/whatsapp-ingest/views/whatsappConfig.html'
        };
    }]);

    return app;

});
