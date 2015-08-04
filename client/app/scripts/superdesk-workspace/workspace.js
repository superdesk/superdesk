
(function() {
    'use strict';

    angular.module('superdesk.workspace', [])
        .service('workspaces', WorkspaceService)
        .directive('sdDeskDropdown', WorkspaceDropdownDirective)
        .directive('sdEditWorkspace', EditWorkspaceDirective)
        ;

    WorkspaceService.$inject = ['api', 'desks', 'session', 'preferencesService', '$q'];
    function WorkspaceService(api, desks, session, preferences, $q) {

        this.active = null;
        this.create = create;
        this.save = save;
        this.setActive = setActiveWorkspace;
        this.setActiveDesk = setActiveDesk;
        this.getActive = getActiveWorkspace;
        this.getActiveId = getActiveWorkspaceId;
        this.queryUserWorkspaces = queryUserWorkspaces;

        var PREFERENCE_KEY = 'workspace:active',
            RESOURCE = 'workspaces',
            self = this;

        function save(workspace) {
            return api.save(RESOURCE, workspace).then(updateActive);
        }

        /**
         * Start editing of new custom workspace
         *
         * @return {Promise}
         */
        function create() {
            var workspace = {user: session.identity._id};
            return workspace;
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
            return api.query(RESOURCE, {where: {desk: deskId}}).then(function(result) {
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
                scope.edited = null;

                scope.afterSave = function(workspace) {
                    desks.setCurrentDeskId(null);
                    workspaces.setActive(workspace);
                    scope.selected = workspace;
                };

                scope.selectDesk = function(desk) {
                    reset();
                    scope.selected = desk;
                    desks.setCurrentDeskId(desk._id);
                    workspaces.setActiveDesk(desk);
                };

                scope.selectWorkspace = function(workspace) {
                    reset();
                    scope.selected = workspace;
                    desks.setCurrentDeskId(null);
                    workspaces.setActive(workspace);
                };

                scope.createWorkspace = function() {
                    scope.edited = workspaces.create();
                };

                function reset() {
                    $location.search('_id', null);
                }

                // init
                function initialize() {
                    workspaces.getActiveId().then(function(activeId) {
                        desks.initialize().then(function() {
                            desks.fetchCurrentUserDesks().then(function(userDesks) {
                                scope.desks = userDesks._items;
                                if (!activeId) {
                                    scope.selected = _.find(scope.desks, {_id: desks.activeDeskId});
                                }
                            });
                        });

                        workspaces.queryUserWorkspaces().then(function(_workspaces) {
                            scope.workspaces = _workspaces;
                            if (activeId) {
                                scope.selected = _.find(scope.workspaces, {_id: activeId});
                            }
                        });
                    });
                }

                //initialize();
                scope.$watch(function() {
                    return workspaces.active;
                }, initialize, true);
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
