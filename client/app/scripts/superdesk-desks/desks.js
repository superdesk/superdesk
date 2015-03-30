/**
 * This file is part of Superdesk.
 *
 * Copyright 2013, 2014 Sourcefabric z.u. and contributors.
 *
 * For the full copyright and license information, please see the
 * AUTHORS and LICENSE files distributed with this source code, or
 * at https://www.sourcefabric.org/superdesk/license
 */

 (function() {
    'use strict';

    DeskListController.$inject = ['$scope', 'desks', 'superdesk', 'privileges', 'tasks', 'api'];
    function DeskListController($scope, desks, superdesk, privileges, tasks, api) {

        var userDesks;

        desks.initialize()
        .then(function() {
            $scope.desks = desks.desks;
            $scope.deskStages = desks.deskStages;

            desks.fetchCurrentUserDesks().then(function (desk_list) {
                userDesks = desk_list._items;
            });
        });

        $scope.statuses = tasks.statuses;

        api('roles').query().then(function(result) {
            $scope.roles = result._items;
        });

        $scope.privileges = privileges.privileges;

        $scope.views = ['content', 'tasks', 'users'];

        $scope.view = $scope.views[0];

        $scope.setView = function(view) {
            $scope.view = view;
        };

        $scope.isMemberOf = function(desk) {
            return _.find(userDesks, {_id: desk._id});
        };

        $scope.openDeskView = function(desk, target) {
            desks.setCurrentDesk(desk);
            superdesk.intent('view', target);
        };

        $scope.$on('desks:refresh:stages', function(e, deskId) {
            desks.refreshStages().then(function() {
                $scope.deskStages[deskId] = desks.deskStages[deskId];
            });
        });
    }

    StageItemListDirective.$inject = ['search', 'api', 'superdesk', 'desks'];
    function StageItemListDirective(search, api, superdesk, desks) {
        return {
            templateUrl: 'scripts/superdesk-desks/views/stage-item-list.html',
            scope: {
                stage: '=',
                total: '=',
                allowed: '=',
                showEmpty: '=?',
                selected: '=?',
                action: '&'
            },
            link: function(scope, elem) {

                var query = search.query({});
                query.filter({term: {'task.stage': scope.stage}});
                query.size(10);
                var criteria = {source: query.getCriteria()};

                scope.loading = true;

                api('archive').query(criteria).then(function(items) {
                    scope.loading = false;
                    scope.items = items._items;
                    scope.total = items._meta.total;
                }, function() {
                    scope.loading = false;
                });

                scope.open = function(item) {
                    desks.setWorkspace(item.task.desk, item.task.stage);
                    superdesk.intent('read_only', 'content_article', item);
                };
            }
        };
    }

    TaskStatusItemsDirective.$inject = ['search', 'api', 'desks'];
    function TaskStatusItemsDirective(search, api, desks) {
        return {
            templateUrl: 'scripts/superdesk-desks/views/task-status-items.html',
            scope: {
                status: '=',
                desk: '=',
                total: '='
            },
            link: function(scope, elem) {

                scope.users = desks.userLookup;

                var query = search.query({});
                query.filter({and: [
                    {term: {'task.status': scope.status}},
                    {term: {'task.desk': scope.desk}}
                ]});
                query.size(10);
                var criteria = {source: query.getCriteria()};

                scope.loading = true;

                api('archive').query(criteria).then(function(items) {
                    scope.loading = false;
                    scope.items = items._items;
                    scope.total = items._meta.total;
                }, function() {
                    scope.loading = false;
                });

            }
        };
    }

    UserRoleItemListDirective.$inject = ['desks'];
    function UserRoleItemListDirective(desks) {
        return {
            templateUrl: 'scripts/superdesk-desks/views/user-role-items.html',
            scope: {
                role: '=',
                desk: '=',
                total: '='
            },
            link: function(scope, elem) {
                scope.users = desks.deskMembers[scope.desk];
            	scope.total = 0;
            	scope.items = [];
            	_.each(scope.users, function(user, index) {
                    if (scope.role === user.role) {
                        scope.items.push(user);
                        scope.total = scope.total + 1;
                    }
                });
            }
        };
    }

    DeskSettingsController.$inject = ['$scope', 'desks'];
    function DeskSettingsController($scope, desks) {
        desks.initialize()
        .then(function() {
            $scope.desks = desks.desks;
        });
    }

    DeskConfigController.$inject = ['$scope', 'gettext', 'notify', 'desks', 'WizardHandler', 'modal'];
    function DeskConfigController ($scope, gettext, notify, desks, WizardHandler, modal) {

        //expecting $scope.desks to be defined

        $scope.modalActive = false;
        $scope.step = {
            current: null
        };
        $scope.desk = {
            edit: null
        };

        $scope.openDesk = function(step, desk) {
            $scope.desk.edit = desk;
            $scope.modalActive = true;
            $scope.step.current = step;
        };

        $scope.cancel = function() {
            $scope.modalActive = false;
            $scope.step.current = null;
            $scope.desk.edit = null;
        };

        $scope.remove = function(desk) {
            modal.confirm(gettext('Please confirm you want to delete desk.')).then(
                function runConfirmed() {
                    desks.remove(desk).then(
                        function(response) {
                            _.remove($scope.desks._items, desk);
                            notify.success(gettext('Desk deleted.'), 3000);
                        },
                        function(response) {
                            if (angular.isDefined(response.data._message)) {
                                notify.error(gettext('Error: ' + response.data._message));
                            }
                        }
                    );
                }
            );
        };
    }

    AggregatehWidgetCtrl.$inject = ['$scope', 'desks'];
    function AggregatehWidgetCtrl($scope, desks) {

        desks.initialize()
        .then(function() {
            desks.fetchCurrentUserDesks().then(function (desk_list) {
                $scope.desks = desk_list;
            });
            $scope.deskStages = desks.deskStages;
        });

        $scope.selected = null;

        $scope.preview = function(item) {
            $scope.selected = item;
        };

    }

    var app = angular.module('superdesk.desks', [
        'superdesk.users',
        'superdesk.authoring.widgets'
    ]);

    var limits = {
        stage: 15,
        desk: 40
    };

    app
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/desks/', {
                    label: gettext('Master Desk'),
                    description: gettext('Navigate through the newsroom'),
                    templateUrl: 'scripts/superdesk-desks/views/main.html',
                    controller: DeskListController,
                    category: superdesk.MENU_MAIN,
                    privileges: {desks: 1}
                })

                .activity('/settings/desks', {
                    label: gettext('Desks'),
                    controller: DeskSettingsController,
                    templateUrl: 'scripts/superdesk-desks/views/settings.html',
                    category: superdesk.MENU_SETTINGS,
                    priority: -800,
                    privileges: {desks: 1}
                });
        }])
        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('desks', {
                type: 'http',
                backend: {
                    rel: 'desks'
                }
            });
        }])
        .config(['authoringWidgetsProvider', function(authoringWidgetsProvider) {
            authoringWidgetsProvider
                .widget('aggregate', {
                    icon: 'view',
                    label: gettext('Aggregate'),
                    template: 'scripts/superdesk-desks/views/aggregate-widget.html',
                    side: 'left',
                    extended: true,
                    display: {authoring: true, packages: false}
                });
        }])
        .controller('AggregatehWidgetCtrl', AggregatehWidgetCtrl)
        .factory('desks', ['$q', 'api', 'preferencesService', 'userList', 'notify', 'session',
            function($q, api, preferencesService, userList, notify, session) {

                var userDesks, userDesksPromise;

                var _fetchAll = function(endpoint, page, items) {
                    page = page || 1;
                    items = items || [];
                    return api(endpoint)
                    .query({max_results: 200, page: page})
                    .then(function(result) {
                        items = items.concat(result._items);
                        if (result._links.next) {
                            page++;
                            return _fetchAll(endpoint, page, items);
                        }
                        return items;
                    });
                };

            /**
             * Set desks.active which contains both desk and stage
             * refs and is updated only when one of those is changed.
             */
            function setActive(desks) {
                if (desks.active && desks.active.desk === desks.activeDeskId && desks.active.stage === desks.activeStageId) {
                    // pass
                    return;
                }

                desks.active = {
                    desk: desks.activeDeskId,
                    stage: desks.activeStageId
                };
            }

            var desksService = {
                desks: null,
                users: null,
                stages: null,
                deskLookup: {},
                stageLookup: {},
                userLookup: {},
                deskMembers: {},
                deskStages: {},
                loading: null,
                activeDeskId: null,
                activeStageId: null,
                active: {desk: null, stage: null},
                fetchDesks: function() {
                    var self = this;

                    return _fetchAll('desks')
                    .then(function(items) {
                        self.desks = {_items: items};
                        _.each(items, function(item) {
                            self.deskLookup[item._id] = item;
                        });
                    });
                },
                fetchUsers: function() {
                    var self = this;

                    return userList.get(null, 1, 500)
                    .then(function(result) {
                        self.users = result;
                        _.each(result._items, function(user) {
                            self.userLookup[user._id] = user;
                        });
                    });
                },
                fetchStages: function() {
                    var self = this;

                    return _fetchAll('stages')
                    .then(function(items) {
                        self.stages = {_items: items};
                        _.each(items, function(item) {
                            self.stageLookup[item._id] = item;
                        });
                    });
                },
                generateDeskMembers: function() {
                    var self = this;

                    _.each(this.desks._items, function(desk) {
                        self.deskMembers[desk._id] = [];
                        _.each(desk.members, function(member, index) {
                            var user = _.find(self.users._items, {_id: member.user});
                            if (user) {
                                self.deskMembers[desk._id].push(user);
                            }
                        });
                    });

                    return $q.when();
                },
                generateDeskStages: function() {
                    var self = this;

                    this.deskStages = _.groupBy(self.stages._items, 'desk');

                    return $q.when();
                },
                fetchUserDesks: function(user) {
                    return api.get(user._links.self.href + '/desks');
                },

                /**
                 * Fetch current user desks and make sure active desk is present in there
                 */
                fetchCurrentUserDesks: function() {
                    if (userDesks) {
                        return $q.when(userDesks);
                    }

                    if (!userDesksPromise) {
                        userDesksPromise = this.fetchCurrentDeskId() // make sure there will be current desk
                            .then(angular.bind(session, session.getIdentity))
                            .then(angular.bind(this, this.fetchUserDesks))
                            .then(angular.bind(this, function(desks) {
                                userDesks = desks;
                                if (desks._items.length) {
                                    if (!this.activeDeskId || !_.find(desks._items, {_id: this.activeDeskId})) {
                                        this.activeDeskId = desks._items[0]._id;
                                    }
                                } else if (this.activeDeskId) {
                                    this.activeDeskId = null;
                                }
                                setActive(this);
                                return desks;
                            }));
                    }

                    return userDesksPromise;
                },

                fetchCurrentDeskId: function() {
                    var self = this;
                    if (self.activeDeskId) {
                        return $q.when(self.activeDeskId);
                    }

                    return preferencesService.get('desk:last_worked').then(function(result) {
                        if (angular.isDefined(result) && result !== '') {
                            self.activeDeskId = result;
                        }
                    });
                },
                fetchCurrentStageId: function() {
                    var self = this;
                    if (self.activeStageId) {
                        return $q.when(self.activeStageId);
                    }

                    return preferencesService.get('stage:items').then(function(result) {
                        if (angular.isDefined(result)) {
                            self.activeStageId = angular.isArray(result) ? result[0] : result;
                        }
                    });
                },
                getCurrentDeskId: function() {
                	if (this.activeDeskId === 'personal') {
                		return '';
                	} else {
                		return this.activeDeskId;
                	}
                },
                setCurrentDeskId: function(deskId) {
                    if (this.activeDeskId !== deskId) {
                        this.activeDeskId = deskId;
                        this.activeStageId = null;
                        setActive(this);
                        preferencesService.update({
                            'desk:last_worked': this.activeDeskId,
                            'stage:items': [this.activeStageId]
                        }, 'desk:last_worked');
                    }
                },
                getCurrentStageId: function() {
                    return this.activeStageId;
                },
                setCurrentStageId: function(stageId) {
                    if (this.activeStageId !== stageId) {
                        this.activeStageId = stageId;
                        setActive(this);
                        preferencesService.update({
                            'desk:last_worked': this.activeDeskId,
                            'stage:items': [this.activeStageId]
                        }, 'desk:last_worked');
                    }
                },
                fetchCurrentDesk: function() {
                    return api.desks.getById(this.getCurrentDeskId());
                },
                setCurrentDesk: function(desk) {
                    this.setCurrentDeskId(desk ? desk._id : null);
                },
                getCurrentDesk: function() {
                	if (!this.activeDeskId || this.activeDeskId === 'personal') {
                		return {'_id': 'personal'};
                	} else {
                		return this.deskLookup[this.activeDeskId];
                	}
                },
                setWorkspace: function(deskId, stageId) {
                    deskId = deskId || null;
                    stageId = stageId || null;
                    if (this.activeDeskId !== deskId || this.activeStageId !== stageId) {
                        this.activeDeskId = deskId;
                        this.activeStageId = stageId;
                        setActive(this);
                        preferencesService.update({
                            'desk:last_worked': this.activeDeskId,
                            'stage:items': [this.activeStageId]
                        }, 'desk:last_worked');
                    }
                },
                initialize: function() {
                    if (!this.loading) {
                        this.fetchCurrentDeskId();
                        this.fetchCurrentStageId();

                        this.loading = this.fetchDesks()
                            .then(angular.bind(this, this.fetchUsers))
                            .then(angular.bind(this, this.generateDeskMembers))
                            .then(angular.bind(this, this.fetchStages))
                            .then(angular.bind(this, this.generateDeskStages))
                            .then(angular.bind(this, this.initActive));
                    }

                    return this.loading;
                },
                initActive: function() {
                    setActive(this);
                },
                save: function(dest, diff) {
                    return api.save('desks', dest, diff)
                        .then(reset);
                },
                remove: function(desk) {
                    return api.remove(desk)
                        .then(reset);
                },
                refreshStages: function() {
                    return this.fetchStages().then(angular.bind(this, this.generateDeskStages));
                },
                refreshUsers: function() {
                    return this.fetchUsers().then(angular.bind(this, this.generateDeskMembers));
                },
                /**
                 * Get current desk for given item
                 *
                 * @param {Object} item
                 */
                getItemDesk: function(item) {
                    if (item.task && item.task.desk) {
                        return this.deskLookup[item.task.desk] || null;
                    }
                }
            };

            return desksService;

            function reset(res) {
                userDesks = null;
                userDesksPromise = null;
                desksService.loading = null;
                return res;
            }
        }])
        .directive('sdStageItems', StageItemListDirective)
        .directive('sdTaskStatusItems', TaskStatusItemsDirective)
        .directive('sdUserRoleItems', UserRoleItemListDirective)
        .directive('sdDeskConfig', function() {
            return {
                controller: DeskConfigController
            };
        })
        .directive('sdDeskConfigModal', function() {
            return {
                scope: {
                    modalActive: '=active',
                    desk: '=',
                    step: '=',
                    desks: '=',
                    cancel: '&'
                },
                require: '^sdDeskConfig',
                templateUrl: 'scripts/superdesk-desks/views/desk-config-modal.html',
                link: function(scope, elem, attrs, ctrl) {

                }
            };
        })
        .directive('sdFocusElement', [function() {
            return {
                link: function(scope, elem, attrs) {
                    elem.click(function() {
                        _.defer(function() {
                            angular.element(document.querySelector(attrs.target)).focus();
                        });
                    });
                }
            };
        }])
        .directive('sdContentExpiry', [function() {
            return {
                templateUrl: 'scripts/superdesk-desks/views/content-expiry.html',
                scope: {
                  item: '=',
                  preview: '='
                },
                link: function(scope, elem, attrs) {

                    var expiryfield = attrs.expiryfield;
                    scope.ContentExpiry = {
                        Hours: 0,
                        Minutes: 0,
                        Header: 'Content Expiry'
                    };

                    scope.$watch('item', function() {
                        setContentExpiry(scope.item);
                    });

                    scope.$watch('ContentExpiry', function() {
                        if (!scope.item) {
                            scope.item = {};
                        }

                        scope.item[expiryfield] = getTotalExpiryMinutes(scope.ContentExpiry);
                    }, true);

                    function getExpiryHours(inputMin) {
                        return Math.floor(inputMin / 60);
                    }

                    function getExpiryMinutes(inputMin) {
                        return Math.floor(inputMin % 60);
                    }

                    function getTotalExpiryMinutes(contentExpiry) {
                        return (contentExpiry.Hours * 60) + contentExpiry.Minutes;
                    }

                    var setContentExpiry = function(item) {

                        if (expiryfield !== 'content_expiry') {
                            scope.ContentExpiry.Header = 'Spike Expiry';
                        }

                        if (item && item[expiryfield] != null) {
                            scope.ContentExpiry.Hours = getExpiryHours(item[expiryfield]);
                            scope.ContentExpiry.Minutes = getExpiryMinutes(item[expiryfield]);
                        }
                    };
                }
            };
        }])
        .directive('sdDeskeditBasic', ['gettext', 'desks', 'WizardHandler', function(gettext, desks, WizardHandler) {
            return {

                link: function(scope, elem, attrs) {

                    scope.limits = limits;

                    scope.$watch('step.current', function(step) {
                        if (step === 'general') {
                            if (scope.desk.edit && scope.desk.edit._id) {
                                scope.edit(scope.desk.edit);
                            }
                            scope.message = null;
                        }
                    });

                    scope.edit = function(desk) {
                        scope.desk.edit = _.create(desk);
                    };

                    scope.save = function(desk) {
                        scope.message = gettext('Saving...');

                        var _new = desk._id ? false : true;
                        desks.save(scope.desk.edit, desk).then(function() {
                            if (_new) {
                                scope.edit(scope.desk.edit);
                                scope.desks._items.unshift(scope.desk.edit);
                            } else {
                                var origDesk = _.find(scope.desks._items, {_id: scope.desk.edit._id});
                                _.extend(origDesk, scope.desk.edit);
                            }
                            WizardHandler.wizard('desks').next();
                        }, errorMessage);
                    };

                    function errorMessage(response) {
                        if (response.data && response.data._issues && response.data._issues.name && response.data._issues.name.unique) {
                            scope._errorUniqueness = true;
                        } else {
                            scope._error = true;
                        }
                        scope.message = null;
                    }

                    function clearErrorMessages() {
                        if (scope._errorUniqueness || scope._error || scope._errorLimits) {
                            scope._errorUniqueness = null;
                            scope._error = null;
                            scope._errorLimits = null;
                        }
                    }

                    scope.handleEdit = function($event) {
                        clearErrorMessages();
                        if (scope.desk.edit.name != null) {
                            scope._errorLimits = scope.desk.edit.name.length > scope.limits.desk ? true : null;
                        }
                    };

                }
            };
        }])
        .directive('sdDeskeditStages', ['gettext', 'api', 'WizardHandler', 'tasks', '$rootScope',
            function(gettext, api, WizardHandler, tasks, $rootScope) {
            return {

                link: function(scope, elem, attrs) {

                    var orig = null;

                    scope.limits = limits;

                    scope.statuses = tasks.statuses;

                    scope.$watch('step.current', function(step, previous) {
                        if (step === 'stages') {
                            scope.editStage = null;
                            orig = null;
                            scope.stages = [];
                            scope.selected = null;
                            scope.message = null;

                            if (scope.desk.edit && scope.desk.edit._id) {
                                scope.message = null;
                                api('stages').query({where: {desk: scope.desk.edit._id}})
                                .then(function(result) {
                                    scope.stages = result._items;
                                });
                            } else {
                                WizardHandler.wizard('desks').goTo(previous);
                            }
                        }
                    });

                    scope.previous = function() {
                        WizardHandler.wizard('desks').previous();
                    };

                    scope.next = function() {
                        WizardHandler.wizard('desks').next();
                    };

                    scope.edit = function(stage) {
                        if (stage.is_visible == null) {
                            stage.is_visible = true;
                        }

                        orig = stage;
                        scope.editStage = _.create(stage);
                        if (!scope.editStage._id) {
                            var lastStage = _.last(scope.stages);
                            if (lastStage) {
                                scope.editStage.task_status = lastStage.task_status;
                            }
                        }
                    };

                    scope.isActive = function(stage) {
                        return scope.editStage && scope.editStage._id === stage._id;
                    };

                    scope.cancel = function() {
                        scope.editStage = null;
                        clearErrorMessages();
                    };

                    scope.select = function(stage) {
                        if (scope.editStage && scope.editStage._id !== stage._id) {
                            return false;
                        }

                        scope.selected = stage;
                    };

                    scope.setStatus = function(status) {
                        scope.editStage.task_status = status._id;
                    };

                    scope.save = function() {
                        if (!orig._id) {
                            _.extend(scope.editStage, {desk: scope.desk.edit._id});
                            api('stages').save({}, scope.editStage)
                            .then(function(item) {
                                scope.stages.push(item);
                                scope.editStage = null;
                                scope.select(item);
                                scope.message = null;
                                broadcastChange();
                            }, errorMessage);
                        } else {
                            api('stages').save(orig, scope.editStage)
                            .then(function(item) {
                                scope.editStage = null;
                                scope.message = null;
                                scope.select(item);
                                broadcastChange();
                            }, errorMessage);
                        }
                    };

                    function errorMessage(response) {
                        if (response.data && response.data._issues && response.data._issues.name && response.data._issues.name.unique) {
                            scope._errorUniqueness = true;
                        } else {
                            scope._error = true;
                        }
                        scope.message = null;
                    }

                    scope.handleEdit = function($event) {
                        clearErrorMessages();
                        if (scope.editStage.name != null) {
                            scope._errorLimits = scope.editStage.name.length > scope.limits.stage ? true : null;
                        }
                    };

                    function clearErrorMessages() {
                        if (scope._errorUniqueness || scope._error || scope._errorLimits) {
                            scope._errorUniqueness = null;
                            scope._error = null;
                            scope._errorLimits = null;
                        }
                    }

                    scope.remove = function(stage) {
                        api('stages').remove(stage)
                        .then(function() {
                            if (stage === scope.selected) {
                                scope.selected = null;
                            }
                            _.remove(scope.stages, stage);
                            scope.message = null;
                            broadcastChange(stage._id);
                        }, function(result) {
                            scope.message = gettext('There was a problem, stage was not deleted.');
                        });
                    };

                    function broadcastChange(stageId, action) {
                        $rootScope.$broadcast('desks:refresh:stages', scope.desk.edit._id);
                    }
                }
            };
        }])
        .directive('sdUserSelectList', ['$filter', 'api', function($filter, api) {
            return {
                scope: {
                    exclude: '=',
                    onchoose: '&'
                },
                templateUrl: 'scripts/superdesk-desks/views/user-select.html',
                link: function(scope, elem, attrs) {

                    var ARROW_UP = 38, ARROW_DOWN = 40, ENTER = 13;

                    scope.selected = null;
                    scope.search = null;
                    scope.users = {};
                    scope.exclude = [];

                    var _refresh = function() {
                        scope.users = {};
                        return api('users').query({where: JSON.stringify({
                            '$or': [
                                {username: {'$regex': scope.search, '$options': '-i'}},
                                {first_name: {'$regex': scope.search, '$options': '-i'}},
                                {last_name: {'$regex': scope.search, '$options': '-i'}},
                                {email: {'$regex': scope.search, '$options': '-i'}}
                            ]
                        })})
                        .then(function(result) {
                            scope.users = result;
                            scope.users._items = _.filter(scope.users._items, function(item) {
                                return _.findIndex(scope.exclude, {_id: item._id}) === -1;
                            });
                            scope.selected = null;
                        });
                    };
                    var refresh = _.debounce(_refresh, 1000);

                    scope.$watch('search', function() {
                        if (scope.search) {
                            refresh();
                        }
                    });

                    function getSelectedIndex() {
                        if (scope.selected) {
                            return _.findIndex(scope.users._items, scope.selected);
                        } else {
                            return -1;
                        }
                    }

                    function previous() {
                        var selectedIndex = getSelectedIndex();
                        if (selectedIndex > 0) {
                            scope.select(scope.users._items[_.max([0, selectedIndex - 1])]);
                        }
                    }

                    function next() {
                        var selectedIndex = getSelectedIndex();
                        scope.select(scope.users._items[_.min([scope.users._items.length - 1, selectedIndex + 1])]);
                    }

                    elem.bind('keydown keypress', function(event) {
                        scope.$apply(function() {
                            switch (event.which) {
                                case ARROW_UP:
                                    event.preventDefault();
                                    previous();
                                    break;
                                case ARROW_DOWN:
                                    event.preventDefault();
                                    next();
                                    break;
                                case ENTER:
                                    event.preventDefault();
                                    if (getSelectedIndex() >= 0) {
                                        scope.choose(scope.selected);
                                    }
                                    break;
                            }
                        });
                    });

                    scope.choose = function(user) {
                        scope.onchoose({user: user});
                        scope.search = null;
                    };

                    scope.select = function(user) {
                        scope.selected = user;
                    };
                }
            };
        }])
        .directive('sdDeskeditPeople', ['gettext', 'WizardHandler', 'desks',  '$rootScope',
            function(gettext, WizardHandler, desks, $rootScope) {
            return {
                link: function(scope, elem, attrs) {

                    scope.$watch('step.current', function(step, previous) {
                        if (step === 'people') {
                            scope.search = null;
                            scope.deskMembers = [];
                            scope.message = null;

                            if (scope.desk.edit && scope.desk.edit._id) {
                                desks.fetchUsers().then(function(result) {
                                    scope.users = desks.users._items;
                                    scope.deskMembers = desks.deskMembers[scope.desk.edit._id] || [];
                                });
                            } else {
                                WizardHandler.wizard('desks').goTo(previous);
                            }
                        }
                    });

                    scope.add = function(user) {
                        scope.deskMembers.push(user);
                    };

                    scope.remove = function(user) {
                        _.remove(scope.deskMembers, user);
                    };

                    scope.previous = function() {
                        WizardHandler.wizard('desks').previous();
                    };

                    scope.save = function() {
                        var members = _.map(scope.deskMembers, function(obj) {
                            return {user: obj._id};
                        });

                        desks.save(scope.desk.edit, {members: members}).then(function(result) {
                            _.extend(scope.desk.edit, result);
                            desks.deskMembers[scope.desk.edit._id] = scope.deskMembers;
                            var origDesk = desks.deskLookup[scope.desk.edit._id];
                            _.extend(origDesk, scope.desk.edit);
                            WizardHandler.wizard('desks').finish();
                        }, function(response) {
                            scope.message = gettext('There was a problem, members not saved.');
                        });
                    };
                }
            };
        }])
        .directive('sdDeskStageMacroPicker', ['desks', 'macros', function(desks, macros) {
            return {
                scope: {
                    desk: '=',
                    stage: '=',
                    macro: '='
                },
                templateUrl: 'scripts/superdesk-desks/views/deskstagemacropicker.html',
                link: function(scope, elem, attrs) {
                    scope.desks = null;
                    scope.deskStages = null;
                    scope.deskMacros = null;

                    scope.$watchGroup(['desk', 'stage'], function() {
                        if (!scope.desks || !scope.deskStages) {
                            desks.initialize()
                            .then(function() {
                                scope.desks = desks.desks._items;
                                scope.deskStages = desks.deskStages;
                            });
                        } else if (scope.desk) {
                            macros.getByDesk(desks.deskLookup[scope.desk].name).then(function(macros) {
                                scope.deskMacros = macros;
                            });

                            if (_.findIndex(scope.deskStages[scope.desk], {_id: scope.stage}) === -1) {
                                scope.stage = null;
                            }
                        }
                    });
                }
            };
        }])
        .directive('sdDeskMacros', ['macros', function (macros) {
            return {
                link: function(scope) {
                    if (scope.desk && scope.desk.edit) {
                        macros.getByDesk(scope.desk.edit.name).then(function(macros) {
                            scope.macros = macros;
                        });
                    }
                }
            };
        }]);

        return app;
})();
