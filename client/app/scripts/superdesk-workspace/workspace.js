
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
        this.getActiveId = getActiveWorkspaceId;
        this.queryUserWorkspaces = queryUserWorkspaces;

        var PREFERENCE_KEY = 'workspace:active',
            RESOURCE = 'workspaces',
            self = this;

        function save(workspace) {
            workspace.user = workspace.user || session.identity._id;
            return api.save(RESOURCE, workspace).then(updateActive);
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
         * Set active workspace for given desk
         *
         * @param {Object} desk
         * @return {Promise}
         */
        function setActiveDesk(desk) {
            setActiveWorkspace(null);
            return getDeskWorkspace(desk._id, desk.name).then(updateActive);
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
                return prefs && prefs.workspace ? prefs.workspace : null;
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
            return desks.fetchCurrentDeskId()
                .then(getActiveWorkspaceId)
                .then(function(activeId) {
                    if (activeId) {
                        return findWorkspace(activeId);
                    } else if (desks.activeDeskId) {
                        return getDeskWorkspace(desks.activeDeskId);
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
            return api.query('desks', {where: {desk: deskId}}).then(function(result) {
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

    WorkspaceDropdownDirective.$inject = ['desks', 'workspaces', '$route', 'preferencesService', '$location', 'reloadService'];
    function WorkspaceDropdownDirective(desks, workspaces, $route, preferencesService, $location, reloadService) {
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

                // init
                function initialize() {
                    var activeId = null;
                    workspaces.getActiveId()
                    .then(function(id) {
                        activeId = id;
                    })
                    .then(angular.bind(desks, desks.initialize))
                    .then(angular.bind(desks, desks.fetchCurrentUserDesks))
                    .then(function(userDesks) {
                        scope.desks = userDesks._items;
                    })
                    .then(workspaces.queryUserWorkspaces)
                    .then(function(_workspaces) {
                        scope.wsList = _workspaces;
                        if (activeId) {
                            scope.selected = _.find(scope.wsList, {_id: activeId});
                            scope.workspaceType = 'workspace';
                        } else {
                            scope.selected = _.find(scope.desks, {_id: desks.getCurrentDeskId()});
                            scope.workspaceType = 'desk';
                        }
                    });
                }

                scope.$watch(function() {
                    return workspaces.active;
                }, initialize, true);
            }
        };
    }

    WorkspaceSidenavDirective.$inject = [];
    function WorkspaceSidenavDirective() {
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
                    var flags = scope.$parent.flags;

                    if (flags.authoring && state) {
                        e.preventDefault();
                        flags.hideMonitoring = !flags.hideMonitoring;
                    } else {
                        flags.hideMonitoring = false;
                    }
                };
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
