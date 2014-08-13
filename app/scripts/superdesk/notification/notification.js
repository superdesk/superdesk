define([
    'angular'
], function(angular) {
    'use strict';

    WebSocketProxy.$inject = ['$rootScope', 'config'];
    function WebSocketProxy($rootScope, config) {

        var ws = new WebSocket(config.server.ws);

    	ws.onmessage = function(event) {
    		var msg = angular.fromJson(event.data);
            console.info('ws', msg);
    		$rootScope.$broadcast(msg.event, msg);
    	};

    	ws.onerror = function(event) {
    		console.error(event);
    	};
    }

    return angular.module('superdesk.notification', [])
    	.run(WebSocketProxy);
});
