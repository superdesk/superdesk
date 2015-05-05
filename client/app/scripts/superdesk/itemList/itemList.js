(function() {

'use strict';

var DEFAULT_OPTIONS = {
    endpoint: 'search',
    pageSize: 25,
    page: 1,
    sort: [{_updated: 'desc'}]
};

angular.module('superdesk.itemList', ['superdesk.search'])
.service('itemListService', ['api', '$q', 'search', function(api, $q, search) {
    function getQuery(options) {
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
            options.urgency ||
            options.savedSearch
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
        var dateKeys = {creationDate: '_created', modificationDate: '_updated'};
        var dateQuery = null;
        _.each(dateKeys, function(key, field) {
            if (options[field + 'Before'] || options[field + 'After']) {
                dateQuery = {};
                dateQuery[key] = {
                    lte: options[field + 'Before'] || undefined,
                    gte: options[field + 'After'] || undefined
                };
                query.source.query.filtered.filter.and.push({range: dateQuery});
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
                queryContent.push(dbField + ':(*' + options[field] + '*)');
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

        // Process related items only search
        if (options.related === true) {
            var queryRelatedItem = [];
            var queryWords = [];
            queryWords = options.keyword.split(' ');
            var length = queryWords.length;
            queryRelatedItem.push('slugline' + ':("' + options.keyword + '")');

            for (var i = 0; i < length; i++) {
                if (options.keyword) {
                    queryRelatedItem.push('slugline' + ':(' + queryWords[i] + ')');
                }
            }

            if (queryRelatedItem.length) {
                query.source.query.filtered.query = {
                    query_string: {
                        query: queryRelatedItem.join(' '),
                        lenient: false,
                        default_operator: 'OR'
                    }
                };
            }
        }

        // process search
        if (options.search) {
            var queryContentAny = [];
            _.each(_.values(fields), function(dbField) {
                queryContentAny.push(dbField + ':(*' + options.search + '*)');
            });
            query.source.query.filtered.query = {
                query_string: {
                    query: queryContentAny.join(' '),
                    lenient: false,
                    default_operator: 'OR'
                }
            };
        }

        // process saved search
        if (options.savedSearch && options.savedSearch._links) {
            return api.get(options.savedSearch._links.self.href).then(function(savedSearch) {
                var criteria = search.query(savedSearch.filter.query).getCriteria();

                query.source.query.filtered.filter.and = query.source.query.filtered.filter.and.concat(
                    criteria.query.filtered.filter.and
                );

                query.source.post_filter = criteria.post_filter;

                return query;
            });
        }

        return query;
    }

    this.fetch = function(options) {
        options = _.extend({}, DEFAULT_OPTIONS, options);
        return $q.when(getQuery(options)).then(function(query) {
            return api(options.endpoint, options.endpointParam || undefined)
                .query(query);
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
.factory('itemPinService', ['preferencesService', function(preferencesService) {
    var PREF_KEY = 'pinned:items';

    var itemPinService = {
        items: null,
        listeners: {ingest: [], archive: []},
        load: function() {
            var self = this;

            return preferencesService.get(PREF_KEY)
            .then(function(result) {
                self.items = result;
            }).then(function() {
                self.updateListeners();
            });
        },
        save: function() {
            var self = this;

            this.items = _.uniq(this.items, function(item) {return item._id;});
            var update = {};
            update[PREF_KEY] = this.items;
            return preferencesService.update(update, PREF_KEY)
            .then(function() {
                self.updateListeners();
            });
        },
        get: function(type) {
            return _.filter(this.items, {_type: type});
        },
        add: function(type, item) {
            var self = this;

            item._type = type;
            this.load()
            .then(function() {
                self.items.push(item);
                return self.save();
            })
            .then(function() {
                self.updateListeners();
            });
        },
        remove: function(item) {
            var self = this;

            this.load()
            .then(function() {
                _.remove(self.items, {_id: item._id});
                return self.save();
            })
            .then(function() {
                self.updateListeners();
            });
        },
        isPinned: function(type, item) {
            return !!_.find(this.items, {_type: type, _id: item._id});
        },
        addListener: function(type, listener) {
            this.listeners[type].push(listener);
            listener(this.get(type));
        },
        removeListener: function(type, listener) {
            _.remove(this.listeners[type], function(i) {
                return i === listener;
            });
        },
        updateListeners: function() {
            var self = this;

            _.each(this.listeners, function(listeners, type) {
                _.each(listeners, function(listener) {
                    listener(self.get(type));
                });
            });
        }
    };
    itemPinService.load();

    return itemPinService;
}])
.directive('sdItemListWidget', ['ItemList', 'notify', 'itemPinService', 'gettext', '$timeout',
function(ItemList, notify, itemPinService, gettext, $timeout) {
    return {
        scope: {
            options: '=',
            itemListOptions: '=',
            actions: '='
        },
        templateUrl: 'scripts/superdesk/itemList/views/item-list-widget.html',
        link: function(scope, element, attrs) {
            scope.items = null;
            scope.processedItems = null;
            scope.maxPage = 1;
            scope.pinnedItems = [];
            scope.selected = null;

            var oldSearch = null;

            var itemList = new ItemList();

            var timeout;

            function refresh() {
                $timeout.cancel(timeout);
                timeout = $timeout(function() {
                    itemList.fetch();
                }, 100, false);
            }

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
                itemPinService.add(scope.options.pinMode, _.clone(item));
            };

            scope.unpin = function(item) {
                itemPinService.remove(item);
            };

            scope.isPinned = function(item) {
                return itemPinService.isPinned(scope.options.pinMode, item);
            };

            var processItems = function() {
                if (scope.items) {
                    if (scope.options.pinEnabled) {
                        scope.processedItems = scope.pinnedItems.concat(scope.items._items);
                    } else {
                        scope.processedItems = scope.items._items;
                    }
                }
            };

            var itemListListener = function() {
                scope.maxPage = itemList.maxPage;
                scope.items = itemList.result;
                processItems();
            };
            var pinListener = function(pinnedItems) {
                scope.pinnedItems = pinnedItems;
                _.each(scope.pinnedItems, function(item) {
                    item.pinnedInstance = true;
                });
                processItems();
            };

            itemList.addListener(itemListListener);
            itemPinService.addListener(scope.options.pinMode, pinListener);
            scope.$on('$destroy', function() {
                itemList.removeListener(itemListListener);
                itemPinService.removeListener(pinListener);
            });

            scope.$watch('itemListOptions', function() {
                itemList.setOptions(scope.itemListOptions);
                refresh();
            }, true);

            scope.$watch('options.similar', function() {
                if (scope.options.similar && scope.options.item) {
                    if (!scope.options.item.slugline) {
                        notify.error(gettext('Error: Keywords required.'));
                        scope.options.similar = false;
                    } else {
                        oldSearch = scope.itemListOptions.search;
                        scope.itemListOptions.search = scope.options.item.slugline;
                    }
                } else {
                    scope.itemListOptions.search = oldSearch || null;
                }
            });
        }
    };
}])
.directive('sdRelatedItemListWidget', ['ItemList', 'notify', 'itemPinService', 'gettext',
function(ItemList, notify, itemPinService, gettext) {
    return {
        scope: {
            options: '=',
            itemListOptions: '=',
            actions: '='
        },
        templateUrl: 'scripts/superdesk/itemList/views/relatedItem-list-widget.html',
        link: function(scope, element, attrs) {
            scope.items = null;
            scope.processedItems = null;
            scope.maxPage = 1;
            scope.pinnedItems = [];
            scope.selected = null;

            var oldSearch = null;

            var itemList = new ItemList();

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
                itemPinService.add(scope.options.pinMode, _.clone(item));
            };

            scope.unpin = function(item) {
                itemPinService.remove(item);
            };

            scope.isPinned = function(item) {
                return itemPinService.isPinned(scope.options.pinMode, item);
            };

            var processItems = function() {
                if (scope.items) {
                    if (scope.options.pinEnabled) {
                        scope.processedItems = scope.pinnedItems.concat(scope.items._items);
                    } else {
                        scope.processedItems = scope.items._items;
                    }
                }
            };

            var itemListListener = function() {
                scope.maxPage = itemList.maxPage;
                scope.items = itemList.result;
                processItems();
            };
            var pinListener = function(pinnedItems) {
                scope.pinnedItems = pinnedItems;
                _.each(scope.pinnedItems, function(item) {
                    item.pinnedInstance = true;
                });
                processItems();
            };

            itemList.addListener(itemListListener);
            itemPinService.addListener(scope.options.pinMode, pinListener);
            scope.$on('$destroy', function() {
                itemList.removeListener(itemListListener);
                itemPinService.removeListener(pinListener);
            });

            scope.$watch('itemListOptions', function() {
                itemList.setOptions(scope.itemListOptions);
                itemList.setOptions({related: scope.options.related});
                refresh();
            }, true);

            scope.$watch('options.related', function() {
                if (scope.options.related && scope.options.item) {
                    if (!scope.options.item.slugline) {
                        notify.error(gettext('Error: Keywords required.'));
                        scope.options.related = false;
                    } else {
                        oldSearch = scope.itemListOptions.keyword;
                        scope.itemListOptions.keyword = scope.options.item.slugline;
                    }
                } else {
                    scope.itemListOptions.keyword = oldSearch || null;
                }
            });
        }
    };
}]);

})();
