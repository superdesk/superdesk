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

    AggregateCtrl.$inject = ['$scope', 'api', 'desks', 'workspaces', 'preferencesService', 'storage', 'gettext', 'multi'];
    function AggregateCtrl($scope, api, desks, workspaces, preferencesService, storage, gettext, multi) {
        var PREFERENCES_KEY = 'agg:view';
        var defaultMaxItems = 10;
        var self = this;
        this.loading = true;
        this.selected = null;
        this.groups = [];
        this.spikeGroups = [];
        this.modalActive = false;
        this.searchLookup = {};
        this.deskLookup = {};
        this.stageLookup = {};
        this.fileTypes = ['all', 'text', 'picture', 'composite', 'video', 'audio'];
        this.selectedFileType = [];
        this.monitoringSearch = false;
        this.searchQuery = null;

        desks.initialize()
        .then(angular.bind(this, function() {
            return desks.fetchCurrentUserDesks()
                .then(angular.bind(this, function (deskList) {
                    this.desks = deskList._items;
                    this.deskLookup = desks.deskLookup;
                    this.deskStages = desks.deskStages;
                    _.each(this.desks, function(desk) {
                        _.each(self.deskStages[desk._id], function(stage) {
                            self.stageLookup[stage._id] = stage;
                        });
                    });
                }));
        }))
        .then(angular.bind(this, function() {
            return api.query('all_saved_searches', {})
               .then(angular.bind(this, function(searchesList) {
                   this.searches = searchesList._items;
                   _.each(this.searches, function(item) {
                       self.searchLookup[item._id] = item;
                   });
               }));
        }))
        .then(angular.bind(this, function() {
            return this.readSettings()
                .then(angular.bind(this, function(groups) {
                    initGroups(groups);
                    setupCards();
                    this.loading = false;
                }));
        }));

        /**
         * If view showed as widget set the current widget
         *
         *@param {object} widget
         */
        this.setWidget = function(widget) {
            this.widget = widget;
        };

        /**
         * Read the setting for current selected workspace(desk or custom workspace)
         * If the view is showed in a widget, read the settings from widget configuration
         * If the current selected workspace is a desk the settings are read from desk
         * If the current selected workspace is a custom workspace the settings are read from
         * user preferences
         * @returns {Object} promise - when resolved return the list of settings
         */
        this.readSettings = function() {
            if (self.widget) {
                return workspaces.readActive()
                .then(function(workspace) {
                    var groups = [];
                    self.widget.configuration = self.widget.configuration || {groups: [], label: ''};
                    _.each(workspace.widgets, function(widget) {
                        if (widget.configuration && self.widget._id === widget._id && self.widget.multiple_id === widget.multiple_id) {
                            groups = widget.configuration.groups || groups;
                            self.widget.configuration.label = widget.configuration.label || '';
                        }
                    });
                    return groups;
                });
            } else {
                return workspaces.getActiveId()
                    .then(function(activeWorkspace) {
                        if (activeWorkspace.type === 'workspace') {
                            return preferencesService.get(PREFERENCES_KEY)
                                .then(function(preference) {
                                    if (preference && preference[activeWorkspace.id] && preference[activeWorkspace.id].groups) {
                                        return preference[activeWorkspace.id].groups;
                                    }
                                });
                        } else if (activeWorkspace.type === 'desk') {
                            var desk = self.deskLookup[activeWorkspace.id];
                            if (desk && desk.monitoring_settings) {
                                return desk.monitoring_settings;
                            }
                        }
                        return [];
                    });
            }
        };

        /**
         * Init groups by filter out from groups stages or saved searches that
         * are not available(deleted or no right on them for stages only) and return all
         * stages for current desk if monitoring setting is not set
         **/
        function initGroups(groups) {
            if (self.groups.length > 0) {
                self.groups.length = 0;
            }
            if (!groups || groups.length === 0) {
                _.each(self.stageLookup, function(item) {
                    if (item.desk === desks.getCurrentDeskId()) {
                        self.groups.push({_id: item._id, type: 'stage', header: item.name});
                    }
                });
            } else {
                _.each(groups, function(item) {
                    if (item.type === 'stage' && !self.stageLookup[item._id]) {
                        return;
                    }
                    if (item.type === 'search' && !self.searchLookup[item._id]) {
                        return;
                    }
                    self.groups.push(item);
                });
            }
            initSpikeGroups();
            updateFileTypeCriteria();
            self.search(self.searchQuery);
        }

        /**
         * Init the spike desks based on already initialized groups
         */
        function initSpikeGroups() {
            var spikeDesks = {};
            if (self.spikeGroups.length > 0) {
                self.spikeGroups.length = 0;
            }
            if (self.groups.length === 0) {
                return;
            }
            _.each(self.groups, function(item, index) {
                if (item.type === 'stage') {
                    var stage = self.stageLookup[item._id];
                    spikeDesks[stage.desk] = self.deskLookup[stage.desk];
                } else if (item.type === 'personal') {
                    spikeDesks.personal = {_id: 'personal', name: 'personal'};
                }
            });
            _.each(spikeDesks, function(item) {
                if (item._id === 'personal') {
                    self.spikeGroups.push({_id: item._id, type: 'spike-personal', header: item.name});
                } else {
                    self.spikeGroups.push({_id: item._id, type: 'spike', header: item.name});
                }
            });
        }

        /**
         * Refresh view after setup
         */
        function refresh() {
            if (self.loading) {
                return null;
            }
            return self.readSettings()
                .then(function(groups) {
                    initGroups(groups);
                    setupCards();
                });
        }

        this.refreshGroups = refresh;

        /**
         * Read the settings when the current workspace
         * selection is changed
         */
        $scope.$watch(function() {
            return workspaces.active;
        }, refresh);

        /**
         * Return true if the 'fileType' filter is selected
         * param {string} fileType
         * @return boolean
         */
        this.hasFileType = function(fileType) {
            if (fileType === 'all') {
                return this.selectedFileType.length === 0;
            }
            return this.selectedFileType.indexOf(fileType) > -1;
        };

        /**
         * Return selected file types if the 'fileType' filter(s) is selected
         * @return [{string}] fileType
         */
        this.getSelectedFileTypes = function() {
            return (this.selectedFileType.length === 0) ? null: JSON.stringify(this.selectedFileType);
        };

        /**
         * Update the type filter criteria
         */
        function updateFileTypeCriteria() {
            var value = (self.selectedFileType.length === 0) ? null: JSON.stringify(self.selectedFileType);

            _.each(self.groups, function(item) {
                item.fileType = value;
            });
            _.each(self.spikeGroups, function(item) {
                item.fileType = value;
            });
        }

        /**
         * Set the current 'fileType' filter
         * param {string} fileType
         */
        this.setFileType = function(fileType) {
            multi.reset();
            if (fileType === 'all') {
                this.selectedFileType = [];
            } else {
                var index = this.selectedFileType.indexOf(fileType);
                if (index > -1) {
                    this.selectedFileType.splice(index, 1);
                } else {
                    this.selectedFileType.push(fileType);
                }
            }
            updateFileTypeCriteria();
        };

        /**
         * Add card metadata into current groups
         */
        function setupCards() {
            var cards = self.groups;
            angular.forEach(cards, setupCard);
            self.cards = cards;

            /**
             * Add card metadata into group
             */
            function setupCard(card) {
                if (card.type === 'stage') {
                    var stage = self.stageLookup[card._id];
                    var desk = self.deskLookup[stage.desk];
                    card.header = desk.name;
                    card.subheader = stage.name;
                }

                if (card.type === 'search') {
                    card.search = self.searchLookup[card._id];
                    card.header = card.search.name;
                }

                if (card.type === 'personal') {
                    card.header = gettext('Personal');
                }
            }
        }

        this.preview = function(item) {
            this.selected = item;
        };

        /**
         * For edit monitoring settings add desk groups to the list
         */
        this.edit = function() {
            this.editGroups = {};
            _.each(this.groups, function(item, index) {
                self.editGroups[item._id] = {
                    _id: item._id,
                    selected: true,
                    type: item.type,
                    max_items: item.max_items || defaultMaxItems,
                    order: index
                };
                if (item.type === 'stage') {
                    var stage = self.stageLookup[item._id];
                    self.editGroups[stage.desk] = {
                        _id: stage._id,
                        selected: true,
                        type: 'desk',
                        order: 0
                    };
                }
            });
            this.modalActive = true;
        };

        /**
         * Set the search set by user on all groups
         */
        this.search = function(query) {
            this.searchQuery = query;
            _.each(this.groups, function(item) {
                item.query = query;
            });
            _.each(this.spikeGroups, function(item) {
                item.query = query;
            });
        };

        /**
         * Reset on all groups the search set by user
         */
        this.resetSearch = function() {
            this.searchQuery = null;
            _.each(this.groups, function(item) {
                item.query = null;
            });
            _.each(this.spikeGroups, function(item) {
                item.query = null;
            });
        };

        this.state = storage.getItem('agg:state') || {};
        this.state.expanded = this.state.expanded || {};

        this.switchExpandedState = function(key) {
            this.state.expanded[key] = !this.getExpandedState(key);
            storage.setItem('agg:state', this.state);
        };

        this.getExpandedState = function(key) {
            return (this.state.expanded[key] === undefined) ? true : this.state.expanded[key];
        };

        this.setSoloGroup = function(group) {
            this.state.solo = group;
            storage.setItem('agg:state', this.state);
        };

        this.getMaxHeightStyle = function(maxItems) {
            var maxHeight = 32 * (maxItems || defaultMaxItems) + 6;
            return {'max-height':  maxHeight.toString() + 'px'};
        };
    }

    AggregateSettingsDirective.$inject = ['desks', 'workspaces', 'session', 'preferencesService', 'WizardHandler'];
    function AggregateSettingsDirective(desks, workspaces, session, preferencesService, WizardHandler) {
        return {
            templateUrl: 'scripts/superdesk-desks/views/aggregate-settings-configuration.html',
            scope: {
                modalActive: '=',
                desks: '=',
                deskStages: '=',
                searches: '=',
                deskLookup: '=',
                stageLookup: '=',
                searchLookup: '=',
                groups: '=',
                editGroups: '=',
                onclose: '&',
                widget: '='
            },
            link: function(scope, elem) {

                var PREFERENCES_KEY = 'agg:view';
                var defaultMaxItems = 10;

                scope.step = {
                    current: 'desks'
                };

                scope.$watch('step.current', function(step) {
                    if (step === 'searches') {
                        scope.initSavedSearches(scope.showAllSavedSearches);
                    }
                });

                scope.showAllSavedSearches = false;
                scope.currentSavedSearches = [];

                scope.closeModal = function() {
                    scope.step.current = 'desks';
                    scope.modalActive = false;
                    scope.showAllSavedSearches = false;
                    scope.onclose();
                };

                scope.previous = function() {
                    WizardHandler.wizard('aggregatesettings').previous();
                };

                scope.next = function() {
                    WizardHandler.wizard('aggregatesettings').next();
                };

                scope.cancel = function() {
                    scope.closeModal();
                };

                scope.setDeskInfo = function(_id) {
                    var item = scope.editGroups[_id];
                    item._id = _id;
                    item.type = 'desk';
                    item.order = 0;
                };

                scope.setStageInfo = function(_id) {
                    var item = scope.editGroups[_id];
                    if (!item.type) {
                        item._id = _id;
                        item.type = 'stage';
                        item.max_items = defaultMaxItems;
                        item.order = _.size(scope.editGroups);
                    }
                };

                scope.setSearchInfo = function(_id) {
                    var item = scope.editGroups[_id];
                    if (!item.type) {
                        item._id = _id;
                        item.type = 'search';
                        item.max_items = defaultMaxItems;
                        item.order = _.size(scope.editGroups);
                    }
                };

                scope.setPersonalInfo = function() {
                    var item = scope.editGroups.personal;
                    if (!item.type) {
                        item._id = 'personal';
                        item.type = 'personal';
                        item.max_items = defaultMaxItems;
                        item.order = _.size(scope.editGroups);
                    }
                };

                /**
                 * Init searches list with all searches if allSearches is true or
                 * user saved searches and other user saved searches
                 * if they are already selected
                 */
                scope.initSavedSearches = function(showAllSavedSearches) {
                    var user = session.identity._id;
                    scope.showAllSavedSearches = showAllSavedSearches;
                    if (scope.currentSavedSearches.length > 0) {
                        scope.currentSavedSearches.length = 0;
                    }
                    _.each(scope.searches, function(item) {
                        var group = scope.editGroups[item._id];
                        if (scope.showAllSavedSearches || item.user === user || group && group.selected) {
                            scope.currentSavedSearches.push(item);
                        }
                    });
                };

                /**
                 * Return the list of selected groups (stages, personal or saved searches)
                 * @return {Array} list of groups
                 */
                scope.getValues = function() {
                    var values = Object.keys(scope.editGroups).map(function(key) {
                        return scope.editGroups[key];
                    });
                    values = _.filter(values, function(item) {
                        if (item.type === 'desk' || !item.selected) {
                            return false;
                        }
                        if (item.type === 'stage') {
                            var stage = scope.stageLookup[item._id];
                            return scope.editGroups[stage.desk].selected;
                        }
                        if (item.type === 'personal') {
                            return scope.editGroups.personal.selected;
                        }
                        return true;
                    });
                    values = _.sortBy(values, function(item) {
                        return item.order;
                    });
                    return values;
                };

                scope.reorder = function(start, end) {
                    var values = scope.getValues();
                    if (end.index !== start.index) {
                        values.splice(end.index, 0, values.splice(start.index, 1)[0]);
                        _.each(values, function(item, index) {
                            item.order = index;
                        });
                    }
                };

                scope.save = function() {
                    var groups = [];
                    _.each(scope.getValues(), function(item, index) {
                        if (item.selected && item.type !== 'desk') {
                            groups.push({
                                _id: item._id,
                                type: item.type,
                                max_items: item.max_items
                            });
                        }
                    });

                    if (scope.widget) {
                        workspaces.getActive()
                        .then(function(workspace) {
                            var widgets =  angular.copy(workspace.widgets);
                            _.each(widgets, function(widget) {
                                if (scope.widget._id === widget._id && scope.widget.multiple_id === widget.multiple_id) {
                                    widget.configuration = {};
                                    widget.configuration.groups = groups;
                                    if (scope.widget.configuration.label) {
                                        widget.configuration.label = scope.widget.configuration.label;
                                    }
                                }
                            });
                            workspaces.save(workspace, {'widgets': widgets})
                            .then(function() {
                                scope.showAllSavedSearches = false;
                                scope.onclose();
                            });
                        });
                    } else {
                        workspaces.getActiveId()
                        .then(function(activeWorkspace) {
                            if (activeWorkspace.type === 'workspace') {
                                preferencesService.get(PREFERENCES_KEY)
                                .then(function(preferences) {
                                    var updates = {};
                                    if (preferences) {
                                        updates[PREFERENCES_KEY] = preferences;
                                    }
                                    updates[PREFERENCES_KEY][activeWorkspace.id] = {groups: groups};
                                    preferencesService.update(updates, PREFERENCES_KEY)
                                    .then(function() {
                                        WizardHandler.wizard('aggregatesettings').finish();
                                    });
                                });
                            } else if (activeWorkspace.type === 'desk'){
                                desks.save(scope.deskLookup[activeWorkspace.id], {monitoring_settings: groups})
                                .then(function() {
                                    WizardHandler.wizard('aggregatesettings').finish();
                                });
                            }
                        });
                        scope.showAllSavedSearches = false;
                        scope.onclose();
                    }
                };
            }
        };
    }

    function SortGroupsDirective() {
        return {
            link: function(scope, element) {

                var updated = false;

                element.sortable({
                    items: '.sort-item',
                    cursor: 'move',
                    containment: '.groups',
                    tolerance: 'pointer',
                    placeholder: {
                        element: function(current) {
                            var height = current.height() - 20;
                            return $('<li class="placeholder" style="height:' + height + 'px"></li>')[0];
                        },
                        update: function() {
                            return;
                        }
                    },
                    start: function(event, ui) {
                        ui.item.data('start_index', ui.item.parent().find('li.sort-item').index(ui.item));
                    },
                    stop: function(event, ui) {
                        if (updated) {
                            updated = false;
                            var start = {
                                index: ui.item.data('start_index')
                            };
                            var end = {
                                index: ui.item.parent().find('li.sort-item').index(ui.item)
                            };
                            ui.item.remove();
                            scope.reorder(start, end);
                            scope.$apply();
                        }
                    },
                    update: function(event, ui) {
                        updated = true;
                    },
                    cancel: '.fake'
                });
            }
        };
    }

    angular.module('superdesk.aggregate', ['superdesk.authoring.widgets', 'superdesk.desks', 'superdesk.workspace'])
    .controller('AggregateCtrl', AggregateCtrl)
    .directive('sdAggregateSettings', AggregateSettingsDirective)
    .directive('sdSortGroups', SortGroupsDirective);

})();
