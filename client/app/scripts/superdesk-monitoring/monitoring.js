(function() {

    'use strict';

    angular.module('superdesk.monitoring', ['superdesk.api', 'superdesk.aggregate', 'superdesk.search', 'superdesk.ui'])
        .service('cards', CardsService)
        .controller('Monitoring', MonitoringController)
        .directive('sdMonitoringView', MonitoringViewDirective)
        .directive('sdMonitoringGroup', MonitoringGroupDirective)
        .directive('sdMonitoringGroupHeader', MonitoringGroupHeader)
        .directive('sdDeskNotifications', DeskNotificationsDirective)
        .directive('sdItemActionsMenu', ItemActionsMenu)
        .config(configureMonitoring)
        .config(configureSpikeMonitoring)
        .config(configurePersonal);

    configureMonitoring.$inject = ['superdeskProvider'];
    function configureMonitoring(superdesk) {
        superdesk
            .activity('/workspace/monitoring', {
                label: gettext('Monitoring'),
                priority: 100,
                templateUrl: 'scripts/superdesk-monitoring/views/monitoring.html',
                topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
                sideTemplateUrl: 'scripts/superdesk-workspace/views/workspace-sidenav.html'
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
                sideTemplateUrl: 'scripts/superdesk-workspace/views/workspace-sidenav.html'
            });
    }

    /**
     * Configure personal option from left menu
     */
    configurePersonal.$inject = ['superdeskProvider'];
    function configurePersonal(superdesk) {
        superdesk
            .activity('/workspace/personal', {
                label: gettext('Personal'),
                priority: 100,
                templateUrl: 'scripts/superdesk-monitoring/views/personal.html',
                topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
                sideTemplateUrl: 'scripts/superdesk-workspace/views/workspace-sidenav.html'
            });
    }

    CardsService.$inject = ['api', 'search', 'session', 'desks'];
    function CardsService(api, search, session, desks) {
        this.criteria = getCriteria;
        this.shouldUpdate = shouldUpdate;

        /**
         * Get items criteria for given card
         *
         * Card can be stage/personal/saved search.
         * There can be also extra string search query
         *
         * @param {Object} card
         * @param {string} queryString
         */
        function getCriteria(card, queryString, queryParam) {
            var params = {};

            if (card.type === 'search' && card.search && card.search.filter.query) {
                params = card.search.filter.query;
                if (card.query) {
                    if (card.search.filter.query.q) {
                        params.q = '(' + card.query + ') ' + card.search.filter.query.q;
                    } else {
                        params.q = '(' + card.query + ') ';
                    }
                }
            } else {
                params.q = card.query;
            }

            params.spike = (card.type === 'spike' || card.type === 'spike-personal');

            var query = search.query(params);

            switch (card.type) {
            case 'search':
                break;

            case 'spike-personal':
            case 'personal':
                query.filter({bool: {
                    must: {term: {original_creator: session.identity._id}},
                    must_not: {exists: {field: 'task.desk'}}
                }});
                break;

            case 'spike':
                query.filter({term: {'task.desk': card._id}});
                break;

            case 'highlights':
                query.filter({and: [
                    {term: {'highlights': queryParam.highlight}}
                ]});
                break;

            case 'deskOutput':
                var desk_id = card._id.substring(0, card._id.indexOf(':'));
                var desk = desks.deskLookup ? desks.deskLookup[desk_id] : null;
                if (desk) {
                    if (desk.desk_type === 'authoring') {
                        query.filter({or: [
                            {term: {'task.last_authoring_desk': desk_id}},
                            {and: [
                                {term: {'task.desk': desk_id}},
                                {terms: {state: ['scheduled', 'published', 'corrected', 'killed']}}
                            ]}
                        ]});
                    } else if (desk.desk_type === 'production') {
                        query.filter({and: [
                            {term: {'task.desk': desk_id}},
                            {terms: {state: ['scheduled', 'published', 'corrected', 'killed']}}
                        ]});
                    }
                }
                break;

            default:
                if (card.singleViewType != null && card.singleViewType === 'desk') {
                    query.filter({term: {'task.desk': card.deskId}});
                } else {
                    query.filter({term: {'task.stage': card._id}});
                }
                break;
            }

            if (card.fileType) {
                query.filter({terms: {'type': JSON.parse(card.fileType)}});
            }

            if (queryString) {
                query.filter({query: {query_string: {query: queryString, lenient: false}}});
            }

            var criteria = {source: query.getCriteria()};
            if (card.type === 'search' && card.search && card.search.filter.query.repo) {
                criteria.repo = card.search.filter.query.repo;
            } else if (card.type === 'deskOutput') {
                criteria.repo = 'archive,published';
            }

            criteria.source.from = 0;
            criteria.source.size = card.max_items || 25;
            return criteria;
        }

        function shouldUpdate(card, data) {
            switch (card.type) {
            case 'stage':
                // refresh stage if it matches updated stage
                return !!data.stages[card._id];

            case 'personal':
                return data.user === session.identity._id;

            default:
                // no way to determine if item should be visible, refresh
                return true;
            }
        }

    }

    MonitoringController.$inject = ['$location', 'desks'];
    function MonitoringController($location, desks) {
        this.state = {};

        this.preview = preview;
        this.closePreview = closePreview;
        this.previewItem = null;

        this.selectedGroup = null;
        this.bindedItems = [];

        this.singleGroup = null;
        this.viewSingleGroup = viewSingleGroup;
        this.viewMonitoringHome = viewMonitoringHome;

        this.queryParam = $location.search();

        this.edit = edit;
        this.editItem = null;

        this.totalItems = '';

        this.isDeskChanged = function () {
            return desks.changeDesk;
        };

        this.highlightsDeskChanged = function () {
            if (desks.changeDesk) {
                $location.url('/workspace/monitoring');
            }
        };

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

        function viewSingleGroup(group, type) {
            group.singleViewType = type;
            vm.singleGroup = group;
        }

        function viewMonitoringHome() {
            vm.singleGroup.singleViewType = null;
            vm.singleGroup = null;
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
                type: '=',
                state: '='
            }
        };
    }

    function MonitoringGroupHeader() {
        return {
            templateUrl: 'scripts/superdesk-monitoring/views/monitoring-group-header.html'
        };
    }

    MonitoringGroupDirective.$inject = ['cards', 'api', 'authoringWorkspace', '$timeout', 'superdesk',
        'activityService', 'workflowService', 'keyboardManager', 'desks', 'search', 'multi', 'archiveService'];
    function MonitoringGroupDirective(cards, api, authoringWorkspace, $timeout, superdesk, activityService,
            workflowService, keyboardManager, desks, search, multi, archiveService) {

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
            require: ['^sdMonitoringView'],
            scope: {
                group: '=',
                numItems: '=',
                viewType: '='
            },
            link: function(scope, elem, attrs, ctrls) {

                var monitoring = ctrls[0];

                scope.view = 'compact';
                scope.page = 1;
                scope.fetching = false;
                scope.previewingBroadcast = false;
                scope.cacheNextItems = [];
                scope.cachePreviousItems = [];
                scope.limited = (monitoring.singleGroup || scope.group.type === 'highlights') ? false : true;

                /**
                  * Generates Identifier to be used by track by expression.
                  */
                scope.generateTrackByIdentifier = function(item) {
                    return search.generateTrackByIdentifier(item);
                };
                scope.edit = edit;
                scope.select = select;
                scope.preview = preview;
                scope.renderNew = renderNew;
                scope.viewSingleGroup = viewSingleGroup;

                scope.$watchCollection('group', queryItems);
                scope.$on('task:stage', queryItems);
                scope.$on('ingest:update', queryItems);
                scope.$on('item:spike', queryItems);
                scope.$on('item:duplicate', queryItems);
                scope.$on('broadcast:created', function(event, args) {
                    scope.previewingBroadcast = true;
                    queryItems();
                    preview(args.item);
                });
                scope.$on('item:unspike', queryItems);
                scope.$on('$routeUpdate', queryItems);
                scope.$on('broadcast:preview', function(event, args) {
                    scope.previewingBroadcast = true;
                    preview(args.item);
                });

                scope.$on('item:highlight', queryItems);

                scope.$on('content:update', function(event, data) {
                    if (cards.shouldUpdate(scope.group, data)) {
                        scheduleQuery();
                    }
                });

                scope.$on('$destroy', unbindActionKeyShortcuts);

                scope.$watch('selected', function(newVal, oldVal) {
                    if (!newVal && scope.previewingBroadcast) {
                        scope.previewingBroadcast = false;
                    }
                });

                /*
                 * Change between single stage view and grouped view by keyboard
                 * Keyboard shortcut: Ctrl + g
                 */
                keyboardManager.bind('ctrl+g', function () {
                    if (scope.selected) {
                        if (monitoring.singleGroup == null) {
                            monitoring.viewSingleGroup(monitoring.selectedGroup, 'stage');
                        } else {
                            monitoring.viewMonitoringHome();
                        }
                    }
                }, {inputDisabled: false});

                /*
                 * Change between single desk view and grouped view by keyboard
                 * Keyboard shortcut: Ctrl + g
                 */
                keyboardManager.bind('ctrl+alt+g', function () {
                    if (scope.selected) {
                        if (monitoring.singleGroup == null) {
                            monitoring.viewSingleGroup(monitoring.selectedGroup, 'desk');
                        } else {
                            monitoring.viewMonitoringHome();
                        }
                    }
                }, {inputDisabled: false});

                /*
                 * Bind item actions on keyboard shortcuts
                 * Keyboard shortcuts are defined with actions
                 *
                 * @param {Object} item
                 */
                function bindActionKeyShortcuts(item) {
                    // First unbind all binded shortcuts
                    if (monitoring.bindedItems) {
                        unbindActionKeyShortcuts();
                    }

                    var intent = {action: 'list'};
                    superdesk.findActivities(intent, item).forEach(function (activity) {
                        if (activity.keyboardShortcut && workflowService.isActionAllowed(item, activity.action)) {
                            monitoring.bindedItems.push(activity.keyboardShortcut);
                            keyboardManager.bind(activity.keyboardShortcut, function () {
                                if (activity._id === 'mark.item') {
                                    bindMarkItemShortcut();
                                } else {
                                    activityService.start(activity, {data: {item: scope.selected}});
                                }
                            }, {inputDisabled: true});
                        }
                    });
                }

                /*
                 * Bind highlight dropdown action
                 * Keyboard shortcut is defined with action
                 *
                 * @param {Object} item
                 */
                function bindMarkItemShortcut() {
                    elem.find('.active .more-activity-toggle').click();
                    var highlightDropdown = angular.element('.more-activity-menu.open .dropdown-noarrow');

                    highlightDropdown.addClass('open');
                    if (highlightDropdown.find('button').length > 0) {
                        highlightDropdown.find('button:not([disabled])')[0].focus();

                        keyboardManager.push('up', function () {
                            highlightDropdown.find('button:focus').parent('li').prev().children('button').focus();
                        });
                        keyboardManager.push('down', function () {
                            highlightDropdown.find('button:focus').parent('li').next().children('button').focus();
                        });
                    }
                }

                /*
                 * Unbind all item actions
                 */
                function unbindActionKeyShortcuts() {
                    monitoring.bindedItems.forEach(function (item) {
                        keyboardManager.unbind(item);
                    });
                    monitoring.bindedItems = [];
                }

                var queryTimeout;

                /**
                 * Schedule content reload in next 50ms
                 *
                 * In case there is another signal within timeout it will trigger it only once.
                 */
                function scheduleQuery() {
                    $timeout.cancel(queryTimeout);
                    queryTimeout = $timeout(queryItems, 50, false);
                }

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

                function edit(item, lock) {
                    if (item.state !== 'spiked'){
                        if (item._type === 'ingest') {
                            var intent = {action: 'list', type: 'ingest'},
                            activity = superdesk.findActivities(intent, item)[0];

                            activityService.start(activity, {data: {item: item}})
                                .then(function (item) {
                                    authoringWorkspace.edit(item, !lock);
                                    monitoring.preview(null);
                                });
                        } else if (item.type === 'composite' && item.package_type === 'takes') {
                            authoringWorkspace.view(item);
                            monitoring.preview(null);
                        } else if (archiveService.isPublished(item)) {
                            authoringWorkspace.view(item);
                            monitoring.preview(null);
                        } else {
                            authoringWorkspace.edit(item, !lock);
                            monitoring.preview(null);
                        }
                    }
                }

                function select(item) {
                    scope.selected = item;
                    monitoring.selectedGroup = scope.group;
                    monitoring.preview(item);

                    bindActionKeyShortcuts(item);
                }

                function preview(item) {
                    select(item);
                }

                function queryItems() {
                    criteria = cards.criteria(scope.group, null, monitoring.queryParam);
                    criteria.source.size = 0; // we only need to get total num of items
                    scope.loading = true;
                    scope.total = null;

                    if (desks.changeDesk) {
                        desks.changeDesk = false;
                        monitoring.singleGroup = null;
                        multi.reset();
                    }

                    return apiquery().then(function(items) {
                        monitoring.totalItems = items._meta.total;
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

                    if (parseInt(list.style.height, 10) !== Math.min(itemsCount, scope.total) * ITEM_HEIGHT) {
                        list.style.height = (Math.min(itemsCount, scope.total) * ITEM_HEIGHT) + 'px';
                    }

                    criteria.source.from = from;
                    criteria.source.size = to - from;

                    var lookup = multi.getIds();    //Ids of selected items
                    return apiquery().then(function(items) {
                        scope.$on('multi:reset', function(event, args) {
                            lookup = null;
                            _.merge(items._items, args);
                        });

                        scope.$applyAsync(function() {
                            if (scope.total !== items._meta.total) {
                                scope.total = items._meta.total;
                                list.style.height = (scope.total * ITEM_HEIGHT) + 'px';
                            }

                            list.style.paddingTop = (from * ITEM_HEIGHT) + 'px';
                            scope.items = merge(items._items);

                            if (lookup != null) {
                                _.filter(items._items, function(item) {
                                    _.find(lookup, function(selectedId) {
                                        if (selectedId === item._id) {
                                            item.selected = true;
                                        }
                                        return selectedId === item._id;
                                    });
                                });
                            }
                        });
                    });
                }

                /**
                 * Request the data on search or archive endpoints
                 * return {promise} list of items
                 */
                function apiquery() {

                    var provider = 'search';
                    if (scope.group.type === 'search' || scope.group.type === 'deskOutput') {
                        if (criteria.repo && criteria.repo.indexOf(',') === -1) {
                            provider = criteria.repo;
                            if (!angular.isDefined(criteria.source.size)) {
                                criteria.source.size = 25;
                            }
                        }
                    } else {
                        provider = 'archive';
                    }

                    return api.query(provider, criteria);
                }

                function renderNew() {
                    scope.total += scope.newItemsCount;
                    scope.newItemsCount = 0;
                    render();
                }

                function viewSingleGroup(group, type) {
                    monitoring.viewSingleGroup(group, type);
                }

                function merge(newItems) {
                    var next = [],
                        olditems = scope.items || [];
                    angular.forEach(newItems, function(item) {
                        var filter = (item.state === 'ingested') ?
                                        {_id: item._id} : {_id: item._id, _current_version: item._current_version};
                        var old = _.find(olditems, filter);
                        next.push(old ? angular.extend(old, item) : item);
                    });

                    return next;
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
    }

    /**
     * Displays the notifications of the desk of a given stage
     *
     */
    DeskNotificationsDirective.$inject = ['desks', 'deskNotifications', 'authoringWorkspace', '$timeout'];
    function DeskNotificationsDirective(desks, deskNotifications, authoringWorkspace, $timeout) {
        return {
            scope: {stage: '=stage'},
            templateUrl: 'scripts/superdesk-monitoring/views/desk-notifications.html',
            link: function(scope) {

                function init() {
                    scope.desk = desks.stageLookup[scope.stage].desk;
                    scope.notifications = deskNotifications.getNotifications(scope.desk);
                    scope.default_incoming = desks.stageLookup[scope.stage].default_incoming;
                    scope.notificationCount = deskNotifications.getUnreadCount(scope.desk) || 0;
                    scope.deskLookup = desks.deskLookup;
                    scope.stageLookup = desks.stageLookup;

                    // Update the figures if there's a desk mention message
                    if (scope.default_incoming) {
                        scope.$on('desk:mention', function() {
                            $timeout(init, 5000);
                        });
                    }
                }

                /**
                 * Opens the story in the notification
                 * and updates the notification as read
                 *
                 * @param {object} notification The notification to be checked
                 */
                scope.open = function(notification) {
                    authoringWorkspace.view(notification.item);
                };

                /**
                 * Updates the notification as read
                 *
                 * @param {object} notification The notification to be checked
                 */
                scope.acknowledge = function(notification) {
                    deskNotifications.markAsRead(notification, scope.desk);
                    $timeout(init, 5000);
                };

                function getRecipient(notification) {
                    return _.find(notification.recipients, {'desk_id': scope.desk});
                }

                /**
                 * Checks if the given notification is read
                 *
                 * @param {object} notification The notification to be checked
                 * @return {boolean} True if the notification is read by any user
                 */
                scope.isRead = function(notification) {
                    var recipient = getRecipient(notification);
                    return recipient && recipient.read;
                };

                /**
                 * Returns the name of the user who read the notification
                 *
                 * @param {object} notification The notification to be checked
                 * @return {string} Display name of the user
                 */
                scope.readBy = function(notification) {
                    var recipient = getRecipient(notification);
                    if (recipient && recipient.read) {
                        return desks.userLookup[recipient.user_id].display_name;
                    }
                };

                init();
            }
        };
    }

    ItemActionsMenu.$inject = ['superdesk', 'activityService', 'workflowService', 'archiveService'];
    function ItemActionsMenu(superdesk, activityService, workflowService, archiveService) {
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

                    if (!isOpen) {
                        // After close, return focus to parent of selected element
                        angular.element('.media-text.selected').parents('li').focus();
                        angular.element('.dropdown-noarrow.open').removeClass('open');
                    }
                };

                /*
                 * If the item gets locked by another user when the activity menu is open then close the menu
                 * as the actions for locked and unlocked are different.
                 */
                scope.$on('item:lock', function(_e, data) {
                    if (scope.open && scope.item && scope.item._id === data.item) {
                        scope.open = false;
                    }
                });

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
                    return archiveService.getType(item);
                }
            }
        };
    }
})();
