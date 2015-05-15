/**
 * This file is part of Superdesk.
 *
 * Copyright 2015 Sourcefabric z.u. and contributors.
 *
 * For the full copyright and license information, please see the
 * AUTHORS and LICENSE files distributed with this source code, or
 * at https://www.sourcefabric.org/superdesk/license
 */
(function() {
    'use strict';

    WebSocketProxy.$inject = ['$rootScope', 'config'];
    function WebSocketProxy($rootScope, config) {

        if (!config.server.ws) {
            return;
        }

        var ws = new WebSocket(config.server.ws);
        ws.onmessage = wsmessage;
        ws.onerror = wserror;

        function wsmessage(event) {
            var msg = angular.fromJson(event.data);
            $rootScope.$broadcast(msg.event, msg.extra);
        }

        function wserror(event) {
            console.error(event);
        }
    }

    return angular.module('superdesk.notification', [])
        .run(WebSocketProxy);
})();
