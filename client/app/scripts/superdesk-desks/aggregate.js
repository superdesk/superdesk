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

    AggregateCtrl.$inject = ['api', 'session', 'desks', 'preferencesService', 'storage'];
    function AggregateCtrl(api, session, desks, preferencesService, storage) {
        var PREFERENCES_KEY = 'agg:view';
        var self = this;
        this.loading = true;
        this.selected = null;
        this.groups = [];
        this.allStages = null;
        this.modalActive = false;
        this.searchLookup = {};
        this.stageLookup = {};

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
            return preferencesService.get(PREFERENCES_KEY)
                .then(angular.bind(this, function(preference) {
                    this.groups = preference != null && preference.groups ? preference.groups : [];
                    this.loading = false;
                }));
        }));

        this.preview = function(item) {
            this.selected = item;
        };

        this.edit = function() {
            this.editGroups = {};
            _.each(this.groups, function(item, index) {
                self.editGroups[item._id] = {
                    _id: item._id,
                    selected: true,
                    type: item.type,
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

        this.search = function(query) {
            this.query = query;
        };

        this.getGroups = function() {
            if (this.groups.length > 0) {
                return this.groups;
            }
            if (!this.allStages) {
                this.allStages = Object.keys(this.stageLookup).map(function(key) {
                    return {_id: key, type: 'stage'};
                });
            }
            return this.allStages;
        };

        this.state = storage.getItem('agg:state') || {};

        this.switchState = function(key) {
            this.state[key] = !this.getState(key);
            storage.setItem('agg:state', this.state);
        };

        this.getState = function(key) {
            return (this.state[key] === undefined) ? true : this.state[key];
        };
    }

    AggregateSettingsDirective.$inject = ['desks', 'preferencesService', 'WizardHandler'];
    function AggregateSettingsDirective(desks, preferencesService, WizardHandler) {
        return {
            templateUrl: 'scripts/superdesk-desks/views/aggregate-settings.html',
            scope: {
                modalActive: '=',
                desks: '=',
                deskStages: '=',
                searches: '=',
                deskLookup: '=',
                stageLookup: '=',
                searchLookup: '=',
                groups: '=',
                editGroups: '='
            },
            link: function(scope, elem) {

                var PREFERENCES_KEY = 'agg:view';

                scope.step = {
                    current: 'desks'
                };

                scope.closeModal = function() {
                    scope.step.current = 'desks';
                    scope.modalActive = false;
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
                        item.order = _.size(scope.editGroups);
                    }
                };

                scope.setSearchInfo = function(_id) {
                    var item = scope.editGroups[_id];
                    if (!item.type) {
                        item._id = _id;
                        item.type = 'search';
                        item.order = _.size(scope.editGroups);
                    }
                };

                scope.getValues = function() {
                    var values = Object.keys(scope.editGroups).map(function(key) {
                        return scope.editGroups[key];
                    });
                    values = _.filter(values, function(item) {
                        if (item.type === 'desk' || !item.selected) {
                            return false;
                        }
                        if (item.type === 'stage') {
                            var desk = scope.stageLookup[item._id].desk;
                            return scope.editGroups[desk].selected;
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
                    scope.groups.length = 0;
                    _.each(scope.getValues(), function(item, index) {
                        if (item.selected && item.type !== 'desk') {
                            scope.groups.push({_id: item._id, type: item.type});
                        }
                    });

                    var updates = {};
                    updates[PREFERENCES_KEY] = {groups: scope.groups};
                    preferencesService.update(updates, PREFERENCES_KEY)
                        .then(angular.bind(this, function() {
                            WizardHandler.wizard('aggregatesettings').finish();
                        }));
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

    angular.module('superdesk.aggregate.sidebar', ['superdesk.authoring.widgets'])
    .config(['authoringWidgetsProvider', function(authoringWidgetsProvider) {
        authoringWidgetsProvider
        .widget('aggregate', {
            icon: 'view',
            label: gettext('Aggregate'),
            template: 'scripts/superdesk-desks/views/aggregate.html',
            side: 'left',
            extended: true,
            display: {authoring: true, packages: false}
        });
    }])
    .controller('AggregateCtrl', AggregateCtrl)
    .directive('sdAggregateSettings', AggregateSettingsDirective)
    .directive('sdSortGroups', SortGroupsDirective);
})();
