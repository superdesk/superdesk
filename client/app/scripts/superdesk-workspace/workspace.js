
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
        this.edited = null;
        this.create = create;
        this.save = save;
        this.cancelEdit = cancelEdit;
        this.setActive = setActiveWorkspace;
        this.setActiveDesk = setActiveDesk;
        this.getActive = getActiveWorkspace;
        this.getActiveId = getActiveWorkspaceId;
        this.queryUserWorkspaces = queryUserWorkspaces;

        var PREFERENCE_KEY = 'workspace:active',
            RESOURCE = 'workspaces',
            deferEdit,
            vm = this;

        /**
         * Start editing of new custom workspace
         */
        function create() {
            vm.edited = {user: session.identity._id};
            deferEdit = $q.defer();
            return deferEdit.promise;
        }

        /**
         * Resolve edit promise with given workspace
         */
        function resolvePromise(workspace) {
            deferEdit.resolve(workspace);
            vm.edited = null;
            return workspace;
        }

        /**
         * Cancel workspace editing
         */
        function cancelEdit() {
            vm.edited = null;
            deferEdit.reject();
        }

        /**
         * Save currently edited workspace
         */
        function save() {
            return api.save(RESOURCE, vm.edited).then(updateActive).then(resolvePromise);
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
         */
        function setActiveDesk(desk) {
            setActiveWorkspace(null);
            return getDeskWorkspace(desk._id, desk.name).then(updateActive);
        }

        /**
         * Set this.active to given workspace
         *
         * @param {Object} workspace
         */
        function updateActive(workspace) {
            vm.active = workspace || null;
            return workspace;
        }

        /**
         * Get active workspace id
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
         */
        function findWorkspace(workspaceId) {
            return api.find(RESOURCE, workspaceId);
        }

        /**
         * Get workspace for given desk
         *
         * @param {string} deskId
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
                    workspaces.create().then(function() {
                        scope.selected = workspaces.active;
                        desks.setCurrentDeskId(null);
                        scope.workspaces.push(scope.selected);
                    });
                };

                function reset() {
                    $location.search('_id', null);
                    $location.path('/workspace');
                }

                // init
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
        };
    }

    EditWorkspaceDirective.$inject = ['workspaces'];
    function EditWorkspaceDirective(workspaces) {
        return {
            templateUrl: 'scripts/superdesk-workspace/views/edit-workspace-modal.html',
            scope: true,
            link: function(scope) {
                scope.workspaces = workspaces;
            }
        };
    }

})();
