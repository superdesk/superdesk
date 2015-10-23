
(function() {
    'use strict';

    angular.module('superdesk.workspace', ['superdesk.workspace.content'])
        .service('workspaces', WorkspaceService)
        .directive('sdDeskDropdown', WorkspaceDropdownDirective)
        .directive('sdWorkspaceSidenav', WorkspaceSidenavDirective)
        .directive('sdEditWorkspace', EditWorkspaceDirective);

    WorkspaceService.$inject = ['api', 'desks', 'session', 'preferencesService', '$q'];
    function WorkspaceService(api, desks, session, preferences, $q) {

        this.active = null;
        this.save = save;
        this.delete = _delete;
        this.setActive = setActiveWorkspace;
        this.setActiveDesk = setActiveDesk;
        this.getActive = getActiveWorkspace;
        this.getActiveId = readActiveWorkspaceId;
        this.readActive = readActiveWorkspace;
        this.queryUserWorkspaces = queryUserWorkspaces;

        var PREFERENCE_KEY = 'workspace:active',
            RESOURCE = 'workspaces',
            self = this;

        function save(workspace, diff) {
            if (diff) {
                return api.save(RESOURCE, workspace, diff).then(updateActive);
            } else {
                workspace.user = workspace.user || session.identity._id;
                return api.save(RESOURCE, workspace).then(updateActive);
            }
        }

        function _delete(workspace) {
            return api.remove(workspace)
            .then(function() {
                if (!self.active || self.active._id !== workspace._id) {
                    return $q.when();
                }
                return self.queryUserWorkspaces();
            })
            .then(function(items) {
                if (items && items.length) {
                    self.setActive(items[0]);
                } else {
                    self.setActive(null);
                }
                self.getActive();
            });
        }

        /**
         * Set active workspace for given desk
         *
         * @param {Object} desk
         * @return {Promise}
         */
        function setActiveDesk(desk) {
            var updates = {};
            updates[PREFERENCE_KEY] = {workspace: desk._id};
            preferences.update(updates, PREFERENCE_KEY);
            return getDeskWorkspace(desk._id).then(updateActive);
        }

        /**
         * Set active workspace
         *
         * @param {Object} workspace
         */
        function setActiveWorkspace(workspace) {
            updateActive(workspace);
            var updates = {};
            updates[PREFERENCE_KEY] = {workspace: workspace ? workspace._id : ''};
            preferences.update(updates, PREFERENCE_KEY);
        }

        /**
         * Set this.active to given workspace
         *
         * @param {Object} workspace
         * @return {object}
         */
        function updateActive(workspace) {
            self.active = workspace || null;
            return workspace;
        }

        /**
         * Get active workspace id
         *
         * @return {Promise}
         */
        function getActiveWorkspaceId() {
            return preferences.get(PREFERENCE_KEY).then(function(prefs) {
                return (prefs && prefs.workspace) ? prefs.workspace : null;
            });
        }

        /**
         * Get active workspace
         *
         * First it reads preferences to get last workspace id,
         * in case it's not set it opens workspace for active desk.
         *
         * @return {Promise}
         */
        function readActiveWorkspaceId() {
            return desks.initialize()
                .then(getActiveWorkspaceId)
                .then(function(activeId) {
                    var type = null;
                    var id = null;

                    if (desks.activeDeskId && desks.deskLookup[desks.activeDeskId]) {
                        type = 'desk';
                        id = desks.activeDeskId;
                    } else if (activeId && desks.deskLookup[activeId]) {
                        type = 'desk';
                        id = activeId;
                        desks.setCurrentDeskId(activeId);
                    } else if (activeId) {
                        type = 'workspace';
                        id = activeId;
                    } else if (desks.getCurrentDeskId()) {
                        type = 'desk';
                        id = desks.getCurrentDeskId();
                    }

                    self.workspaceType = type;
                    return {'id': id, 'type': type};
                });
        }

        /**
         * Read active workspace
         *
         * First it reads preferences to get last workspace id,
         * in case it's not set it opens workspace for active desk.
         *
         * @return {Promise}
         */
        function readActiveWorkspace() {
            return readActiveWorkspaceId()
                .then(function(activeWorkspace) {
                    if (activeWorkspace.type === 'desk') {
                        return getDeskWorkspace(activeWorkspace.id);
                    } else if (activeWorkspace.type === 'workspace') {
                        return findWorkspace(activeWorkspace.id);
                    }
                });
        }

        /**
         * Get active workspace
         *
         * First it reads preferences to get last workspace id,
         * in case it's not set it opens workspace for active desk.
         *
         * @return {Promise}
         */
        function getActiveWorkspace() {
            return readActiveWorkspaceId()
                .then(function(activeWorkspace) {
                    if (activeWorkspace.type === 'desk') {
                        return getDeskWorkspace(activeWorkspace.id);
                    } else if (activeWorkspace.type === 'workspace') {
                        return findWorkspace(activeWorkspace.id);
                    } else {
                        return createUserWorkspace();
                    }
                }).then(updateActive);
        }

        /**
         * Find workspace by given id
         *
         * @param {string} workspaceId
         * @return {Promise}
         */
        function findWorkspace(workspaceId) {
            return api.find(RESOURCE, workspaceId);
        }

        /**
         * Get workspace for given desk
         *
         * @param {string} deskId
         * @return {Promise}
         */
        function getDeskWorkspace(deskId) {
            return api.query('workspaces', {where: {desk: deskId}}).then(function(result) {
                if (result._items.length === 1) {
                    return result._items[0];
                } else {
                    return {desk: deskId, widgets: []};
                }
            });
        }

        /**
         * Create custom workspace for given user using old config
         *
         * @return {object}
         */
        function createUserWorkspace() {
            return {
                user: session.identity._id,
                // [BC] use old user workspace
                widgets: session.identity.workspace ? session.identity.workspace.widgets : []
            };
        }

        /**
         * Get list of user workspaces
         *
         * @return {Promise}
         */
        function queryUserWorkspaces() {
            return session.getIdentity().then(function(identity) {
                return api.query(RESOURCE, {where: {user: identity._id}});
            }).then(function(response) {
                return response._items;
            });
        }
    }

    WorkspaceDropdownDirective.$inject = ['desks', 'workspaces', '$route', 'preferencesService', '$location', 'reloadService',
    'notifyConnectionService'];
    function WorkspaceDropdownDirective(desks, workspaces, $route, preferencesService, $location, reloadService,
        notifyConnectionService) {
        return {
            templateUrl: 'scripts/superdesk-workspace/views/workspace-dropdown.html',
            link: function(scope) {
                scope.workspaces = workspaces;
                scope.wsList = null;
                scope.edited = null;

                scope.afterSave = function(workspace) {
                    desks.setCurrentDeskId(null);
                    workspaces.setActive(workspace);
                    scope.selected = workspace;
                };

                scope.selectDesk = function(desk) {
                    reset();
                    scope.selected = desk;
                    scope.workspaceType = 'desk';
                    desks.setCurrentDeskId(desk._id);
                    workspaces.setActiveDesk(desk);
                    reloadService.activeDesk = desks.active.desk;
                };

                scope.selectWorkspace = function(workspace) {
                    reset();
                    scope.selected = workspace;
                    scope.workspaceType = 'workspace';
                    desks.setCurrentDeskId(null);
                    workspaces.setActive(workspace);
                };

                scope.createWorkspace = function() {
                    scope.edited = {};
                };

                function reset() {
                    $location.search('_id', null);
                }

                /**
                 * Restore the last desk/current workspace selection
                 */
                function initialize() {
                    var activeWorkspace = null;
                    workspaces.getActiveId()
                    .then(function(workspace) {
                        activeWorkspace = workspace;
                    })
                    .then(angular.bind(desks, desks.fetchCurrentUserDesks))
                    .then(function(userDesks) {
                        scope.desks = userDesks._items;
                    })
                    .then(workspaces.queryUserWorkspaces)
                    .then(function(_workspaces) {
                        scope.wsList = _workspaces;
                        scope.workspaceType = activeWorkspace.type;
                        if (activeWorkspace.type === 'desk') {
                            scope.selected = _.find(scope.desks, {_id: activeWorkspace.id});
                        } else if (activeWorkspace.type === 'workspace') {
                            scope.selected = _.find(scope.wsList, {_id: activeWorkspace.id});
                        } else {
                            scope.selected = null;
                        }
                    });
                }

                scope.$watch(function() {
                    return workspaces.active;
                }, initialize, true);
            }
        };
    }

    WorkspaceSidenavDirective.$inject = ['superdeskFlags', '$location', 'keyboardManager'];
    function WorkspaceSidenavDirective(superdeskFlags, $location, keyboardManager) {
        return {
            templateUrl: 'scripts/superdesk-workspace/views/workspace-sidenav-items.html',
            link: function(scope) {

                /*
                 * Function for showing and hiding monitoring list
                 * while authoring view is opened.
                 *
                 * @param {boolean} state Gets the state of button
                 * @param {object} e Gets $event from the element
                 */
                scope.hideMonitoring = function (state, e) {
                    if (superdeskFlags.flags.authoring && state) {
                        e.preventDefault();
                        superdeskFlags.flags.hideMonitoring = !superdeskFlags.flags.hideMonitoring;
                    } else {
                        superdeskFlags.flags.hideMonitoring = false;
                    }
                };

                /*
                 * By using keyboard shortcuts, change the current showed view
                 *
                 */
                var opt = {global: true, inputDisabled: false};
                keyboardManager.bind('alt+h', function (e) {
                    e.preventDefault();
                    $location.url('/workspace');
                }, opt);
                keyboardManager.bind('alt+m', function (e) {
                    e.preventDefault();
                    $location.url('/workspace/monitoring');
                }, opt);
                keyboardManager.bind('alt+t', function (e) {
                    e.preventDefault();
                    $location.url('/workspace/tasks');
                }, opt);
                keyboardManager.bind('alt+x', function (e) {
                    e.preventDefault();
                    $location.url('/workspace/spike-monitoring');
                }, opt);
                keyboardManager.bind('alt+p', function (e) {
                    e.preventDefault();
                    $location.url('/workspace/personal');
                }, opt);
                keyboardManager.bind('alt+f', function (e) {
                    e.preventDefault();
                    $location.url('search');
                }, opt);
            }
        };
    }

    EditWorkspaceDirective.$inject = ['workspaces'];
    function EditWorkspaceDirective(workspaces) {
        return {
            templateUrl: 'scripts/superdesk-workspace/views/edit-workspace-modal.html',
            scope: {
                workspace: '=',
                done: '='
            },
            link: function(scope) {
                scope.workspaces = workspaces;

                /**
                 * Trigger workspace.save and in case there is an error returned assign it to scope.
                 */
                scope.save = function() {
                    workspaces.save(scope.workspace)
                    .then(function() {
                        scope.errors = null;
                        var workspace = scope.workspace;
                        scope.workspace = null;
                        if (scope.done) {
                            return scope.done(workspace);
                        }
                    }, function(response) {
                        scope.errors = response.data._issues;
                    });
                };

                scope.cancel = function() {
                    scope.workspace = null;
                };
            }
        };
    }

})();
