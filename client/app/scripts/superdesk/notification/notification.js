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

    WebSocketProxy.$inject = ['$rootScope', 'config', 'desks'];
    function WebSocketProxy($rootScope, config, desks, session) {

        var ReloadEvents = [
            'user_disabled',
            'user_inactivated',
            'user_role_changed',
            'user_type_changed',
            'user_privileges_revoked',
            'role_privileges_revoked',
            'desk_membership_revoked',
            'desk',
            'stage',
            'stage_visibility_updated'
        ];

        if (!config.server.ws) {
            return;
        }

        var ws = new WebSocket(config.server.ws);

        ws.onmessage = function(event) {
            var msg = angular.fromJson(event.data);
            $rootScope.$broadcast(msg.event, msg.extra);
            if (_.contains(ReloadEvents, msg.event)) {
                $rootScope.$broadcast('reload', msg);
            }
        };

        ws.onerror = function(event) {
            console.error(event);
        };
    }

    ReloadService.$inject = ['$window', '$rootScope', 'session', 'desks', 'gettext'];
    function ReloadService($window, $rootScope, session, desks, gettext) {
        var _this = this;
        _this.userDesks = [];
        _this.result = null;
        desks.fetchCurrentUserDesks().then(function (desk_list) {
            _this.userDesks = desk_list._items;
        });
        var userEvents = {
            'user_disabled': 'User is disabled',
            'user_inactivated': 'User is inactivated',
            'user_role_changed': 'User role is changed',
            'user_type_changed': 'User type is changed',
            'user_privileges_revoked': 'User privileges are revoked'
        };
        var roleEvents = {
            'role_privileges_revoked': 'Role role_privileges_revoked'
        };
        var deskEvents = {
            'desk_membership_revoked': 'User removed from desk',
            'desk': 'Desk is deleted/updated'
        };
        var stageEvents = {
            'stage': 'Stage is created/updated/deleted',
            'stage_visibility_updated': 'Stage visibility change'
        };

        $rootScope.$on('reload', function(event, msg) {
            _this.result = _this.reloadIdentifier(msg);
            _this.reload(_this.result);
        });
        this.reload = function(result) {
            if (result.reload) {
                if ($window.location.hash != null && $window.location.hash.match('/authoring/') != null) {
                    _this.broadcast(gettext(result.message));
                } else {
                    $window.location.reload(true);
                }
            }
        };

        this.broadcast = function(msg) {
            $rootScope.$broadcast('savework', msg);
        };

        this.reloadIdentifier = function(msg) {
            var result = {
                reload: false,
                message: null
            };
            if (_.has(userEvents, msg.event)) {
                if (msg.extra.user_id != null) {
                    if (msg.extra.user_id.indexOf(session.identity._id)  !== -1) {
                        result.message = userEvents[msg.event];
                        result.reload = true;
                    }
                }
            }

            if (_.has(roleEvents, msg.event)) {
                if (msg.extra.role_id.indexOf(session.identity.role)  !== -1) {
                    result.message = roleEvents[msg.event];
                    result.reload = true;
                }
            }
            if (_.has(deskEvents, msg.event)) {
                if (msg.extra.desk_id != null && msg.extra.user_ids != null) {
                    if (_.find(_this.userDesks, {_id: msg.extra.desk_id}) != null &&
                        msg.extra.user_ids.indexOf(session.identity._id)  !== -1) {
                        result.message = deskEvents[msg.event];
                        result.reload = true;
                    }
                }
            }

            if (_.has(stageEvents, msg.event)) {
                if (msg.extra.desk_id != null) {
                    if (msg.event === 'stage_visibility_updated') {
                        if (_.find(_this.userDesks, {_id: msg.extra.desk_id}) == null &&
                        ($window.location.hash.match('/search') != null || $window.location.hash.match('/authoring/') != null)) {
                            result.message = stageEvents[msg.event];
                            result.reload = true;
                        }
                    } else if (msg.event === 'stage') {
                        if (_.find(_this.userDesks, {_id: msg.extra.desk_id}) != null) {
                            result.message = stageEvents[msg.event];
                            result.reload = true;
                        }
                    }
                }
            }
            return result;
        };
    }

    return angular.module('superdesk.notification', ['superdesk.desks'])
        .service('reloadService', ReloadService)
        .run(WebSocketProxy);
})();
