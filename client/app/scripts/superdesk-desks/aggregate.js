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

    AggregateCtrl.$inject = ['$scope', 'api', 'session', 'desks', 'workspaces', 'preferencesService', 'storage', 'gettext'];
    function AggregateCtrl($scope, api, session, desks, workspaces, preferencesService, storage, gettext) {
        var PREFERENCES_KEY = 'agg:view';
        var defaultMaxItems = 10;
        var self = this;
        this.loading = true;
        this.selected = null;
        this.groups = [];
        this.spikeGroups = null;
        this.allStages = null;
        this.allDesks = null;
        this.modalActive = false;
        this.searchLookup = {};
        this.deskLookup = {};
        this.stageLookup = {};
        this.fileTypes = ['all', 'text', 'picture', 'composite', 'video', 'audio'];
        this.selectedFileType = [];
        this.monitoringSearch = false;

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
            return api.query('saved_searches', {}, session.identity)
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
                    if (groups) {
                        _.each(groups, angular.bind(this, function(item) {
                            this.groups.push(item);
                        }));
                    }
                    setupCards();
                    this.loading = false;
                }));
        }));

        /**
         * Read the setting for current selected workspace(desk or custom workspace)
         * If the current selected workspace is a desk the settings are read from desk
         * If the current selected workspace is a custom workspace the settings are read from
         * user preferences
         * @returns {Object} promise - when resolved return the list of settings
         */
        this.readSettings = function() {
            return workspaces.getActiveId()
                .then(angular.bind(this, function(activeWorkspaceId) {
                    if (activeWorkspaceId) {
                        return preferencesService.get(PREFERENCES_KEY)
                            .then(angular.bind(this, function(preference) {
                                if (preference && preference[activeWorkspaceId] && preference[activeWorkspaceId].groups) {
                                    return preference[activeWorkspaceId].groups;
                                }
                            }));
                    } else {
                        var desk = this.deskLookup[desks.getCurrentDeskId()];
                        if (desk && desk.monitoring_settings) {
                            return desk.monitoring_settings;
                        }
                    }
                    return [];
                }));
        };

        /**
         * Refresh view after setup
         */
        function refresh() {
            if (self.loading) {
                return null;
            }
            return self.readSettings()
                .then(function(groups) {
                    if (self.groups.length) {
                        self.groups.length = 0;
                    }
                    if (groups) {
                        _.each(groups, function(item) {
                            self.groups.push(item);
                        });
                    }
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
         * Set the current 'fileType' filter
         * param {string} fileType
         */
        this.setFileType = function(fileType) {
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

            var value = (this.selectedFileType.length === 0) ? null: JSON.stringify(this.selectedFileType);

            _.each(this.groups, function(item) {
                item.fileType = value;
            });
            if (this.allStages) {
                _.each(this.allStages, function(item) {
                    item.fileType = value;
                });
            }
            if (this.spikeGroups) {
                _.each(this.spikeGroups, function(item) {
                    item.fileType = value;
                });
            }
            if (this.allDesks) {
                _.each(this.allDesks, function(item) {
                    item.fileType = value;
                });
            }
        };

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
                    if (stage) {
                        var desk = self.deskLookup[stage.desk];
                        card.header = desk.name;
                        card.subheader = stage.name;
                    } else {
                        card.header = 'Deleted desk or stage';
                    }
                }

                if (card.type === 'search') {
                    card.search = self.searchLookup[card._id];
                    card.header = card.search ? card.search.name: 'Deleted saved search';
                }

                if (card.type === 'personal') {
                    card.header = gettext('Personal');
                }
            }
        }

        this.preview = function(item) {
            this.selected = item;
        };

        this.edit = function() {
            this.editGroups = {};
            _.each(this.groups, function(item, index) {
                if (item.type === 'search' && !self.searchLookup[item._id]) {
                    return;
                }
                self.editGroups[item._id] = {
                    _id: item._id,
                    selected: true,
                    type: item.type,
                    max_items: item.max_items || defaultMaxItems,
                    order: index
                };
                if (item.type === 'stage') {
                    var stage = self.stageLookup[item._id];
                    if (!stage) {
                        return;
                    }
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

        this.search = function(query) {
            _.each(this.groups, function(item) {
                item.query = query;
            });
            if (this.allStages) {
                _.each(this.allStages, function(item) {
                    item.query = query;
                });
            }
            if (this.spikeGroups) {
                _.each(this.spikeGroups, function(item) {
                    item.query = query;
                });
            }
            if (this.allDesks) {
                _.each(this.allDesks, function(item) {
                    item.query = query;
                });
            }
        };

        this.resetSearch = function() {
            _.each(this.groups, function(item) {
                item.query = null;
            });
            if (this.allStages) {
                _.each(this.allStages, function(item) {
                    item.query = null;
                });
            }
            if (this.spikeGroups) {
                _.each(this.spikeGroups, function(item) {
                    item.query = null;
                });
            }
            if (this.allDesks) {
                _.each(this.allDesks, function(item) {
                    item.query = null;
                });
            }
        };

        /**
         * Creates a list of spike desk groups based on the setting from agg:view property.
         * If a stage is selected the correspondent desk will appear in the result list.
         * If agg:view is not set, all desks will be returned
         * @return [{_id: string, type: string, header:string}]
         */
        this.getSpikeGroups = function() {
            if (this.groups.length > 0) {
                if (!this.spikeGroups) {
                    var spikeDesks = {};
                    _.each(this.groups, function(item, index) {
                        if (item.type === 'stage') {
                            var stage = self.stageLookup[item._id];
                            spikeDesks[stage.desk] = self.deskLookup[stage.desk].name;
                        }
                    });

                    this.spikeGroups = Object.keys(spikeDesks).map(function(key) {
                        return {_id: key, type: 'spike', header: spikeDesks[key]};
                    });
                }
                return this.spikeGroups;
            }

            if (!this.allDesks) {
                this.allDesks = Object.keys(this.deskLookup).map(function(key) {
                    return {_id: key, type: 'spike', header: self.deskLookup[key].name};
                });
            }
            return this.allDesks;
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

    AggregateSettingsDirective.$inject = ['desks', 'workspaces', 'preferencesService', 'WizardHandler'];
    function AggregateSettingsDirective(desks, workspaces, preferencesService, WizardHandler) {
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
                widget: '@'
            },
            link: function(scope, elem) {

                var PREFERENCES_KEY = 'agg:view';
                var defaultMaxItems = 10;

                scope.step = {
                    current: 'desks'
                };

                scope.closeModal = function() {
                    scope.step.current = 'desks';
                    scope.modalActive = false;
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
                            if (!stage || !stage.desk) {
                                return false;
                            }
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

                    var updates = {};
                    workspaces.getActiveId()
                    .then(function(activeWorkspaceId) {
                        if (activeWorkspaceId) {
                            preferencesService.get(PREFERENCES_KEY)
                            .then(function(preferences) {
                                if (preferences) {
                                    updates[PREFERENCES_KEY] = preferences;
                                }
                                updates[PREFERENCES_KEY][activeWorkspaceId] = {groups: groups};
                                preferencesService.update(updates, PREFERENCES_KEY)
                                .then(function() {
                                    WizardHandler.wizard('aggregatesettings').finish();
                                });
                            });
                        } else {
                            desks.save(scope.deskLookup[desks.getCurrentDeskId()], {monitoring_settings: groups})
                            .then(function() {
                                WizardHandler.wizard('aggregatesettings').finish();
                            });
                        }
                    });

                    scope.onclose();
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
