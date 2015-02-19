(function() {

'use strict';

var DEFAULT_OPTIONS = {
    endpoint: 'search',
    pageSize: 25,
    page: 1,
    sort: [{versioncreated: 'desc'}]
};

angular.module('superdesk.itemList', [])
.service('itemListService', ['api', function(api) {
    var getQuery = function(options) {
        var query = {source: {query: {filtered: {}}}};
        // process filter aliases and shortcuts
        if (options.sortField && options.sortDirection) {
            var sort = {};
            sort[options.sortField] = options.sortDirection;
            options.sort = [sort];
        }
        if (options.repo) {
            options.repos = [options.repo];
        }
        // add shared query structure
        if (
            options.types ||
            options.notStates ||
            options.states ||
            options.creationDateBefore ||
            options.creationDateAfter ||
            options.modificationDateBefore ||
            options.modificationDateAfter ||
            options.provider ||
            options.source ||
            options.urgency
        ) {
            query.source.query.filtered.filter = {and: []};
        }
        // process page and pageSize
        query.source.size = options.pageSize;
        query.source.from = (options.page - 1) * options.pageSize;
        // process sorting
        query.source.sort = options.sort;
        // process repo
        if (options.repos) {
            query.repo = options.repos.join(',');
        }
        // process types
        if (options.types) {
            query.source.query.filtered.filter.and.push({terms: {type: options.types}});
        }
        // process notState
        if (options.notStates) {
            _.each(options.notStates, function(notState) {
                query.source.query.filtered.filter.and.push({not: {term: {state: notState}}});
            });
        }
        // process state
        if (options.states) {
            var stateQuery = [];
            _.each(options.states, function(state) {
                stateQuery.push({term: {state: state}});
            });
            query.source.query.filtered.filter.and.push({or: stateQuery});
        }
        // process creation date
        _.each(['creationDate', 'modificationDate'], function(field) {
            if (options[field + 'Before'] || options[field + 'After']) {
                query.source.query.filtered.filter.and.push({range: {firstcreated: {
                    lte: options[field + 'Before'] || undefined,
                    gte: options[field + 'After'] || undefined
                }}});
            }
        });
        // process provider, source, urgency
        _.each(['provider', 'source', 'urgency'], function(field) {
            if (options[field]) {
                var directQuery = {};
                directQuery[field] = options[field];
                query.source.query.filtered.filter.and.push({term: directQuery});
            }
        });

        // process search
        var fields = {
            headline: 'headline',
            subject: 'subject.name',
            keyword: 'slugline',
            uniqueName: 'unique_name',
            body: 'body_html'
        };
        var queryContent = [];
        _.each(fields, function(dbField, field) {
            if (options[field]) {
                queryContent.push(dbField + ':(' + options[field] + ')');
            }
        });
        if (queryContent.length) {
            query.source.query.filtered.query = {
                query_string: {
                    query: queryContent.join(' '),
                    lenient: false,
                    default_operator: 'AND'
                }
            };
        }
        // process search
        if (options.search) {
            var queryContentAny = [];
            _.each(_.values(fields), function(dbField) {
                queryContentAny.push(dbField + ':(' + options.search + ')');
            });
            query.source.query.filtered.query = {
                query_string: {
                    query: queryContentAny.join(' '),
                    lenient: false,
                    default_operator: 'OR'
                }
            };
        }

        return query;
    };
    this.fetch = function(options) {
        options = _.extend(DEFAULT_OPTIONS, options);
        var query = getQuery(options);
        return api(options.endpoint, options.endpointParam || undefined)
            .query(query)
            .then(function(result) {
                return result;
            });
    };
}])
.provider('ItemList', function() {
    this.$get = ['itemListService', function(itemListService) {
        var ItemList = function() {
            this.listeners = [];
            this.options = _.clone(DEFAULT_OPTIONS);
            this.result = {};
            this.maxPage = 0;
        };

        ItemList.prototype.setOptions = function(options) {
            this.options = _.extend(this.options, options);
            return this;
        };

        ItemList.prototype.addListener = function(listener) {
            this.listeners.push(listener);
            return this;
        };

        ItemList.prototype.removeListener = function(listener) {
            _.remove(this.listeners, function(i) {
                return i === listener;
            });
            return this;
        };

        ItemList.prototype.fetch = function() {
            var self = this;

            return itemListService.fetch(this.options)
            .then(function(result) {
                self.result = result;
                self.maxPage = Math.ceil(result._meta.total / self.options.pageSize) || 0;
                _.each(self.listeners, function(listener) {
                    listener(result);
                });
                return result;
            });
        };

        return ItemList;
    }];
})
.directive('sdItemListWidget', ['ItemList', 'preferencesService', function(ItemList, preferencesService) {
    return {
        scope: {
            options: '=',
            itemListOptions: '=',
            actions: '='
        },
        templateUrl: 'scripts/superdesk/itemList/views/item-list-widget.html',
        link: function(scope, element, attrs) {
            scope.items = null;
            scope.maxPage = 1;
            scope.pinnedItems = [];
            scope.selected = null;

            var pinnedList = {};
            var itemList = new ItemList();
            
            itemList.addListener(function() {
                scope.maxPage = itemList.maxPage;
                scope.items = itemList.result;
                processItems();
            });

            scope.$watch('itemListOptions', function() {
                itemList.setOptions(scope.itemListOptions);
                refresh();
            }, true);

            scope.$watch('options', function() {
                if (scope.options.pinEnabled) {
                    loadPinned();
                }
            }, true);

            var _refresh = function() {
                itemList.fetch();
            };
            var refresh = _.debounce(_refresh, 100);

            scope.view = function(item) {
                scope.selected = item;
            };

            scope.toggleItemType = function(itemType) {
                if (scope.itemListOptions.types.indexOf(itemType) > -1) {
                    scope.itemListOptions.types = _.without(scope.itemListOptions.types, itemType);
                } else {
                    scope.itemListOptions.types.push(itemType);
                }
            };

            scope.isItemTypeEnabled = function(itemType) {
                return scope.itemListOptions.types.indexOf(itemType) > -1;
            };

            scope.pin = function(item) {
                var newItem = _.cloneDeep(item);
                newItem.pinnedInstance = true;
                scope.pinnedItems.push(newItem);
                scope.pinnedItems = _.uniq(scope.pinnedItems, '_id');
                pinnedList[item._id] = true;
                savePinned(scope.pinnedItems);
            };

            scope.unpin = function(item) {
                _.remove(scope.pinnedItems, {_id: item._id});
                pinnedList[item._id] = false;
                savePinned(scope.pinnedItems);
            };

            scope.isPinned = function(item) {
                return item && pinnedList[item._id];
            };

            var savePinned = function() {
                preferencesService.update({
                    'pinned:items': scope.pinnedItems
                }, 'pinned:items')
                .then(function() {
                    processItems();
                }, function(response) {
                    notify.error(gettext('Session preference could not be saved...'));
                });
            };

            var loadPinned = function() {
                preferencesService.get('pinned:items')
                .then(function(result) {
                    scope.pinnedItems = result;
                    _.each(scope.pinnedItems, function(item) {
                        pinnedList[item._id] = true;
                    });
                });
            };

            var processItems = function() {
                if (scope.options.pinEnabled && scope.items) {
                    scope.items._items = scope.pinnedItems.concat(scope.items._items);
                }
            };
        }
    };
}]);

})();
