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

    WebSocketProxy.$inject = ['$rootScope', 'config', 'reloadService'];
    function WebSocketProxy($rootScope, config, reloadService) {

        if (!config.server.ws) {
            return;
        }

        var ws = new WebSocket(config.server.ws);

        ws.onmessage = function(event) {
            var msg = angular.fromJson(event.data);
            $rootScope.$broadcast(msg.event, msg.extra);
            reloadService.reload(msg.event);
        };

        ws.onerror = function(event) {
            console.error(event);
        };
    }

    return angular.module('superdesk.notification', [])
        .service('reloadService', ['$window', '$rootScope', function($window, $rootScope) {
            this.reload = function(msgEvent, $location) {
                if (msgEvent === 'desk') {
                    console.log(msgEvent);
                    if ($window.location.hash != null && $window.location.hash.match('/authoring/') != null) {
                        console.log('notification on authoring page');
                        this.broadcast();
                    } else {
                        console.log('notification on non-authoring page');
                        $window.location.reload(true);
                    }
                }
            };

            this.broadcast = function() {
                $rootScope.$broadcast('savework');
            };
        }])
        .run(WebSocketProxy);
})();
