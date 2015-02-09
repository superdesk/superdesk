define(['angular'], function(angular) {
    'use strict';
    var config = {
        server: {
            url: null
        },
        ws: {
            url: null
        }
    };

    return angular.module('superdesk.config', []).constant('config', config);
});
