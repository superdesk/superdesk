(function() {

    'use strict';

    angular.module('superdesk.monitoring', ['superdesk.api', 'superdesk.aggregate', 'superdesk.search'])
        .service('cards', CardsService)
        .controller('Monitoring', MonitoringController)
        .directive('sdMonitoringView', MonitoringViewDirective)
        .directive('sdMonitoringGroup', MonitoringGroupDirective)
        .directive('sdMonitoringGroupHeader', MonitoringGroupHeader)
        .directive('sdItemActionsMenu', ItemActionsMenu)
        .config(configureMonitoring)
        .config(configureSpikeMonitoring);

    configureMonitoring.$inject = ['superdeskProvider'];
    function configureMonitoring(superdesk) {
        superdesk
            .activity('/workspace/monitoring', {
                label: gettext('Monitoring'),
                priority: 100,
                templateUrl: 'scripts/superdesk-monitoring/views/monitoring.html',
                topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
                sideTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-sidenav.html'
            });
    }

    configureSpikeMonitoring.$inject = ['superdeskProvider'];
    function configureSpikeMonitoring(superdesk) {
        superdesk
            .activity('/workspace/spike-monitoring', {
                label: gettext('Spike Monitoring'),
                priority: 100,
                templateUrl: 'scripts/superdesk-monitoring/views/spike-monitoring.html',
                topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
                sideTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-sidenav.html'
            });
    }

    CardsService.$inject = ['api', 'search', 'session'];
    function CardsService(api, search, session) {
        this.criteria = getCriteria;

        /**
         * Get items criteria for given card
         *
         * Card can be stage/personal/saved search.
         * There can be also extra string search query
         *
         * @param {Object} card
         * @param {string} queryString
         */
        function getCriteria(card, queryString) {
            var params = (card.type === 'search') ? JSON.parse(JSON.stringify(card.search.filter.query)): {};
            params.spike = (card.type === 'spike');

            if (card.type === 'search') {
                if (card.query) {
                    params.q = '(' + card.query + ') ' + card.search.filter.query.q;
                }
            } else {
                params.q = card.query;
            }

            var query = search.query(params);

            switch (card.type) {
                case 'search':
                    break;

                case 'personal':
                    query.filter({bool: {
                        must: {term: {original_creator: session.identity._id}},
                        must_not: {exists: {field: 'task.desk'}}
                    }});
                    break;

                case 'spike':
                    query.filter({term: {'task.desk': card._id}});
                    break;

                default:
                    query.filter({term: {'task.stage': card._id}});
                    break;
            }

            if (queryString) {
                query.filter({query: {query_string: {query: queryString, lenient: false}}});
            }

            var criteria = {source: query.getCriteria()};
            criteria.source.from = 0;
            criteria.source.size = 25;
            return criteria;
        }
    }

    function MonitoringController() {
        this.state = {};

        this.preview = preview;
        this.closePreview = closePreview;
        this.previewItem = null;

        this.singleGroup = null;
        this.viewSingleGroup = viewSingleGroup;

        this.edit = edit;
        this.editItem = null;

        var vm = this;

        function preview(item) {
            vm.previewItem = item;
            vm.state['with-preview'] = !!item;
        }

        function closePreview() {
            preview(null);
        }

        function edit(item) {
            vm.editItem = item;
            vm.state['with-authoring'] = !!item;
        }

        function viewSingleGroup(group) {
            vm.singleGroup = group;
        }
    }

    /**
     * Main monitoring view - list + preview
     *
     * it's a directive so that it can be put together with authoring into some container directive
     */
    function MonitoringViewDirective() {
        return {
            templateUrl: 'scripts/superdesk-monitoring/views/monitoring-view.html',
            controller: 'Monitoring',
            controllerAs: 'monitoring',
            scope: {
                type: '='
            }
        };
    }

    function MonitoringGroupHeader() {
        return {
            templateUrl: 'scripts/superdesk-monitoring/views/monitoring-group-header.html'
        };
    }

    MonitoringGroupDirective.$inject = ['cards', 'api', 'superdesk', 'desks', '$timeout'];
    function MonitoringGroupDirective(cards, api, superdesk, desks, $timeout) {
        var ITEM_HEIGHT = 57,
            ITEMS_COUNT = 5,
            BUFFER = 8,
            UP = -1,
            DOWN = 1,
            ENTER_KEY = 13,
            MOVES = {
                38: UP,
                40: DOWN
            };

        return {
            templateUrl: 'scripts/superdesk-monitoring/views/monitoring-group.html',
            require: ['^sdMonitoringView', '^sdAuthoringContainer'],
            scope: {
                group: '=',
                numItems: '='
            },
            link: function(scope, elem, attrs, ctrls) {

                var monitoring = ctrls[0],
                    authoring = ctrls[1];

                scope.view = 'compact';
                scope.page = 1;
                scope.fetching = false;
                scope.cacheNextItems = [];
                scope.cachePreviousItems = [];
                scope.limited = monitoring.singleGroup ? false : true;

                scope.uuid = uuid;
                scope.edit = edit;
                scope.select = select;
                scope.preview = preview;
                scope.renderNew = renderNew;
                scope.viewSingleGroup = viewSingleGroup;

                scope.$watch('group', queryItems);
                scope.$watch('group.query', queryItems);
                scope.$on('task:stage', handleStage);
                scope.$on('ingest:update', update);

                var list = elem[0].getElementsByClassName('inline-content-items')[0],
                    scrollElem = elem.find('.stage-content').first();

                scrollElem.on('keydown', handleKey);
                scrollElem.on('scroll', handleScroll);
                scope.$on('$destroy', function() {
                    scrollElem.off();
                });

                var criteria,
                    updateTimeout,
                    moveTimeout;

                function handleStage(event, data) {
                    if (data.new_stage === scope.stage || data.old_stage === scope.stage) {
                        update();
                    }
                }

                function edit(item) {
                    authoring.edit(item);
                }

                function select(item) {
                    scope.selected = item;
                    monitoring.preview(item);
                }

                function preview(item) {
                    select(item);
                }

                function queryItems() {
                    criteria = cards.criteria(scope.group);
                    criteria.source.size = 0; // we only need to get total num of items
                    scope.loading = true;
                    scope.total = null;
                    return apiquery().then(function(items) {
                        scope.total = items._meta.total;
                        scope.$applyAsync(render);
                    })['finally'](function() {
                        scope.loading = false;
                    });
                }

                function render() {
                    var top = scrollElem[0].scrollTop,
                        start = Math.floor(top / ITEM_HEIGHT),
                        from = Math.max(0, start - BUFFER),
                        itemsCount = scope.numItems || ITEMS_COUNT,
                        to = Math.min(scope.total, start + itemsCount + BUFFER);

                    if (parseInt(list.style.height, 10) !== scope.total * ITEM_HEIGHT) {
                        list.style.height = (scope.total * ITEM_HEIGHT) + 'px';
                    }

                    criteria.source.from = from;
                    criteria.source.size = to - from;
                    return apiquery().then(function(items) {
                        scope.$applyAsync(function() {
                            if (scope.total !== items._meta.total) {
                                scope.total = items._meta.total;
                                list.style.height = (scope.total * ITEM_HEIGHT) + 'px';
                            }

                            list.style.paddingTop = (from * ITEM_HEIGHT) + 'px';
                            scope.items = merge(items._items);
                        });
                    });
                }

                function apiquery(query) {
                    return api.query('archive', query ? {source: query} : criteria);
                }

                function renderNew() {
                    scope.total += scope.newItemsCount;
                    scope.newItemsCount = 0;
                    render();
                }

                function viewSingleGroup(group) {
                    monitoring.viewSingleGroup(group);
                }

                function merge(newItems) {
                    var next = [],
                        olditems = scope.items || [];
                    angular.forEach(newItems, function(item) {
                        var old = _.find(olditems, {_id: item._id});
                        next.push(old ? angular.extend(old, item) : item);
                    });

                    return next;
                }

                function updateCurrentView() {
                    var ids = _.pluck(scope.items, '_id'),
                        query = {query: {filtered: {filter: {and: [
                            {terms: {_id: ids}},
                            {term: {'task.stage': scope.stage}}
                        ]}}}};
                    query.size = ids.length;
                    apiquery(query).then(function(items) {
                        var nextItems = _.indexBy(items._items, '_id');
                        angular.forEach(scope.items, function(item, i) {
                            var diff = nextItems[item._id] || {_deleted: 1};
                            angular.extend(item, diff);
                        });
                    });
                }

                function update() {
                    if (scrollElem[0].scrollTop || scope.selected) {
                        updateCurrentView();
                    } else {
                        render();
                    }
                }

                function handleScroll(event) {
                    $timeout.cancel(updateTimeout);
                    updateTimeout = $timeout(render, 100, false);
                }

                function handleKey(event) {
                    var code = event.keyCode || event.which;
                    if (MOVES[code]) {
                        event.preventDefault();
                        event.stopPropagation();
                        $timeout.cancel(updateTimeout);
                        move(MOVES[code], event);
                        handleScroll(); // make sure we scroll after moving
                    } else if (code === ENTER_KEY) {
                        scope.$applyAsync(function() {
                            edit(scope.selected);
                        });
                    }
                }

                function clickItem(item, event) {
                    scope.select(item);
                    if (event) {
                        event.preventDefault();
                        event.stopPropagation();
                        event.stopImmediatePropagation();
                    }
                }

                function move(diff, event) {
                    var index = _.findIndex(scope.items, scope.selected),
                        itemsCount = scope.numItems || ITEMS_COUNT,
                        nextItem,
                        nextIndex;

                    if (index === -1) {
                        nextItem = scope.items[0];
                    } else {
                        nextIndex = Math.max(0, Math.min(scope.items.length - 1, index + diff));
                        nextItem = scope.items[nextIndex];

                        $timeout.cancel(moveTimeout);
                        moveTimeout = $timeout(function() {
                            var top = scrollElem[0].scrollTop,
                                topItemIndex = Math.ceil(top / ITEM_HEIGHT),
                                bottomItemIndex = Math.floor((top + scrollElem[0].clientHeight) / ITEM_HEIGHT),
                                nextItemIndex = nextIndex + criteria.source.from;
                            if (nextItemIndex < topItemIndex) {
                                scrollElem[0].scrollTop = Math.max(0, nextItemIndex * ITEM_HEIGHT);
                            } else if (nextItemIndex >= bottomItemIndex) {
                                scrollElem[0].scrollTop = (nextItemIndex - itemsCount + 1) * ITEM_HEIGHT;
                            }
                        }, 50, false);
                    }

                    scope.$apply(function() {
                        clickItem(scope.items[nextIndex], event);
                    });
                }
            }
        };

        function uuid(item) {
            return item._id;
        }
    }

    ItemActionsMenu.$inject = ['superdesk', 'activityService', 'workflowService'];
    function ItemActionsMenu(superdesk, activityService, workflowService) {
        return {
            scope: {
                item: '=',
                active: '='
            },
            templateUrl: 'scripts/superdesk-monitoring/views/item-actions-menu.html',
            link: function(scope) {
                /**
                 * Populate scope actions when dropdown is opened.
                 *
                 * @param {boolean} isOpen
                 */
                scope.toggleActions = function(isOpen) {
                    scope.actions = isOpen ? getActions(scope.item) : scope.actions;
                    scope.open = isOpen;
                };

                /**
                 * Stope event propagation so that click on dropdown menu
                 * won't select that item for preview/authoring.
                 *
                 * @param {Event} event
                 */
                scope.stopEvent = function(event) {
                    event.stopPropagation();
                };

                scope.run = function(activity) {
                    return activityService.start(activity, {data: {item: scope.item}});
                };

                /**
                 * Get available actions for given item.
                 *
                 * This is not context aware, it will return everything.
                 *
                 * @param {object} item
                 * @return {object}
                 */
                function getActions(item) {
                    var intent = {action: 'list', type: getType(item)};
                    var groups = {};
                    superdesk.findActivities(intent, item).forEach(function(activity) {
                        if (workflowService.isActionAllowed(scope.item, activity.action)) {
                            var group = activity.group || 'default';
                            groups[group] = groups[group] || [];
                            groups[group].push(activity);
                        }
                    });
                    return groups;
                }

                /**
                 * Get actions type based on item state. Used with activity filter.
                 *
                 * @param {Object} item
                 * @return {string}
                 */
                function getType(item) {
                    if (item.state === 'spiked') {
                        return 'spike';
                    }

                    if (item.state === 'ingested') {
                        return 'ingest';
                    }

                    return 'archive';
                }
            }
        };
    }
})();
