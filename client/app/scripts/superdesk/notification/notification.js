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

    var ReloadIdentifier = {
        'user_disabled': 'User is disabled',
        'user_inactivated': 'User is inactivated',
        'user_role_changed': 'User role is changed',
        'user_type_changed': 'User type is changed',
        'user_privileges_revoked': 'User privileges are revoked',
        'role_privileges_revoked': 'Role role_privileges_revoked',
        'desk_membership_revoked': 'User removed from desk',
        'desk': 'Desk is deleted/updated',
        'stage': 'Stage is created/updated/deleted',
        'stage_visibility_updated': 'Stage visibility change'
    };
    //var userDesks;
    WebSocketProxy.$inject = ['$rootScope', 'config', 'reloadService'];
    function WebSocketProxy($rootScope, config, reloadService) {
        //console.log(session.identity);

        if (!config.server.ws) {
            return;
        }

        var ws = new WebSocket(config.server.ws);

        ws.onmessage = function(event) {
            var msg = angular.fromJson(event.data);
            $rootScope.$broadcast(msg.event, msg.extra);
            if (msg.data !== 'ping') {
                reloadService.reload(msg);
            }
            //reloadService.reload(msg.data);
        };

        ws.onerror = function(event) {
            console.error(event);
        };
    }

    return angular.module('superdesk.notification', [])
        .service('reloadService', ['$window', '$rootScope', 'session', function($window, $rootScope, session) {
           /* desks.fetchCurrentUserDesks().then(function (desk_list) {
                userDesks = desk_list._items;
            });*/
            this.reload = function(msg) {
                if (ReloadIdentifier[msg.event] != null) {
                    console.log('This is RELOAD Event');
                    /*if (msg.extra.desk_id != null) {
                        if (_.find(userDesks, {_id: msg.extra.desk_id}) != null) {
                            console.log('event related to current userdsk event related to current user desk');
                        }
                    }*/
                    if (msg.extra.user_ids != null) {
                        if (msg.extra.user_ids.indexOf(session.identity._id)  !== -1) {
                            console.log('event related to current user');
                        }
                    }
                    if ($window.location.hash != null && $window.location.hash.match('/authoring/') != null) {
                        console.log('notification on authoring page');
                        //this.broadcast(ReloadIdentifier['user_disabled']);
                    } else {
                        console.log('notification on non-authoring page');
                        //$window.location.reload(true);
                    }
                }
            };

            this.broadcast = function(msg) {
                $rootScope.$broadcast('savework', msg);
            };
        }])
        .run(WebSocketProxy);
})();
