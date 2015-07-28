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

    /**
     * Service for highlights with caching.
     */
    HighlightsService.$inject = ['api', '$q', '$cacheFactory', 'packages'];
    function HighlightsService(api, $q, $cacheFactory, packages) {
        var service = {};
        var promise = {};
        var cache = $cacheFactory('highlightList');

        /**
         * Fetches and caches highlights, or returns from the cache.
         */
        service.get = function(desk) {
            var DEFAULT_CACHE_KEY = '_nodesk';
            var key = desk || DEFAULT_CACHE_KEY;
            var value = cache.get(key);

            if (value) {
                return $q.when(value);
            } else if (promise[key]) {
                return promise[key];
            } else {
                var criteria = {};
                if (desk) {
                    criteria = {where: {'$or': [
                                                {'desks': desk},
                                                {'desks': {'$size': 0}}
                                               ]
                                        }
                                };
                }

                promise[key] = api('highlights').query(criteria)
                    .then(function(result) {
                        cache.put(key, result);
                        promise[key] = null;
                        return $q.when(result);
                    });

                return promise[key];
            }
        };

        /**
         * Clear user cache
         */
        service.clearCache = function() {
            cache.removeAll();
            promise = {};
        };

        /**
         * Mark an item for a highlight
         */
        service.markItem = function(highlight, marked_item) {
            return api.markForHighlights.create({highlights: highlight, marked_item: marked_item});
        };

        /**
         * Create empty highlight package
         */
        service.createEmptyHighlight = function(highlight) {
            var pkg_defaults = {
                headline: highlight.name,
                highlight: highlight._id
            };

            var group = null;

            if (highlight.groups && highlight.groups.length > 0) {
                group =  highlight.groups[0];
            }

            return packages.createEmptyPackage(pkg_defaults, group);
        };

        return service;
    }

    MarkHighlightsDropdownDirective.$inject = ['desks', 'highlightsService'];
    function MarkHighlightsDropdownDirective(desks, highlightsService) {
        return {
            templateUrl: 'scripts/superdesk-highlights/views/mark_highlights_dropdown_directive.html',
            link: function(scope) {

                scope.markItem = function(highlight) {
                    highlightsService.markItem(highlight._id, scope.item._id);
                    if (!scope.item.highlights) {
                        scope.item.highlights = [highlight._id];
                    } else {
                        scope.item.highlights = [highlight._id].concat(scope.item.highlights);
                    }
                };

                scope.isMarked = function(highlight) {
                    return scope.item && scope.item.highlights && scope.item.highlights.indexOf(highlight._id) >= 0;
                };

                highlightsService.get(desks.getCurrentDeskId()).then(function(result) {
                    scope.highlights = result._items;
                });
            }
        };
    }

    MultiMarkHighlightsDropdownDirective.$inject = ['desks', 'highlightsService', 'multi'];
    function MultiMarkHighlightsDropdownDirective(desks, highlightsService, multi) {
        return {
            templateUrl: 'scripts/superdesk-highlights/views/mark_highlights_dropdown_directive.html',
            link: function(scope) {

                scope.markItem = function(highlight) {
                    angular.forEach(multi.getItems(), function(item) {
                        if (!item.highlights) {
                            item.highlights = [highlight._id];
                        } else if (item.highlights.indexOf(highlight._id) === -1) {
                            item.highlights = [highlight._id].concat(item.highlights);
                        } else {
                            return;
                        }
                        highlightsService.markItem(highlight._id, item._id);
                    });
                    multi.reset();
                };

                scope.isMarked = function(highlight) {
                    var result = _.find(multi.getItems(), function(item) {
                        return !item.highlights || item.highlights.indexOf(highlight._id) === -1;
                    });
                    return !result;
                };

                highlightsService.get(desks.getCurrentDeskId()).then(function(result) {
                    scope.highlights = result._items;
                });
            }
        };
    }

    HighlightsTitleDirective.$inject = ['highlightsService', '$timeout'];
    function HighlightsTitleDirective(highlightsService, $timeout) {
        return {
            scope: {
                item: '=item',
                orientation: '=?'
            },
            templateUrl: 'scripts/superdesk-highlights/views/highlights_title_directive.html',
            // todo(petr): refactor to use popover-template once angular-bootstrap 0.13 is out
            link: function(scope, elem) {
                var unmarkBox = elem.find('.unmark').hide(),
                    icon = elem.find('i'),
                    isOpen,
                    closeTimeout;

                scope.orientation = scope.orientation || 'right';

                scope.$watch('item.highlights', function(_ids) {
                    if (_ids) {
                        highlightsService.get().then(function(result) {
                            scope.highlights = _.filter(result._items, function(highlight) {
                                return _ids.indexOf(highlight._id) >= 0;
                            });
                            // it has to first update the template before we use its html
                            scope.$applyAsync(function() {
                                scope.htmlTooltip = unmarkBox.html();
                            });
                        });
                    }
                });

                scope.openTooltip = function() {
                    $timeout.cancel(closeTimeout);
                    closeTimeout = null;
                    if (!isOpen) {
                        toggle();
                        isOpen = true;
                    }
                };

                scope.closeTooltip = function() {
                    if (isOpen && !closeTimeout) {
                        closeTimeout = $timeout(function() {
                            toggle();
                            isOpen = false;
                        }, 100, false);
                    }
                };

                function toggle() {
                    $timeout(function() { // need to timeout because tooltip is not expecting $digest
                        icon[0].dispatchEvent(new CustomEvent('toggle'));
                    }, 0, false);
                }

                // ng-click is not working because of tooltip
                elem.on('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    var btn = e.target.nodeName === 'BUTTON' ? e.target : e.target.parentNode;
                    var highlight = btn.attributes['data-highlight'];
                    if (highlight) {
                        unmarkHighlight(highlight.value);
                    }
                });

                function unmarkHighlight(highlight) {
                    highlightsService.mark_item(highlight, scope.item._id).then(function() {
                        scope.item.highlights = _.without(scope.item.highlights, highlight);
                    });
                }
            }
        };
    }

    SearchHighlightsDirective.$inject = ['highlightsService'];
    function SearchHighlightsDirective(highlightsService) {
        return {
            scope: {highlight_id: '=highlight'},
            templateUrl: 'scripts/superdesk-highlights/views/search_highlights_dropdown_directive.html',
            link: function(scope) {
                scope.selectHighlight = function(highlight) {
                    scope.highlight_id = null;
                    if (highlight) {
                        scope.highlight_id = highlight._id;
                    }
                };

                scope.hasHighlights = function() {
                    return _.size(scope.highlights) > 0;
                };

                highlightsService.get().then(function(result) {
                    scope.highlights = result._items;
                });
            }
        };
    }

    PackageHighlightsDropdownDirective.$inject = ['superdesk', 'desks', 'highlightsService'];
    function PackageHighlightsDropdownDirective(superdesk, desks, highlightsService) {
        return {
            templateUrl: 'scripts/superdesk-highlights/views/package_highlights_dropdown_directive.html',
            link: function(scope) {

                scope.createHighlight = function(highlight) {
                    highlightsService.createEmptyHighlight(highlight)
                    .then(function(new_package) {
                        superdesk.intent('author', 'package', new_package);
                    });
                };

                highlightsService.get(desks.getCurrentDeskId()).then(function(result) {
                    scope.highlights = result._items;
                    scope.hasHighlights = _.size(scope.highlights) > 0;
                });
            }
        };
    }

    HighlightsSettingsController.$inject = ['$scope', 'desks'];
    function HighlightsSettingsController($scope, desks) {
        desks.initialize().then(function() {
            $scope.desks = desks.deskLookup;
        });

        $scope.hours = _.range(1, 25);
        $scope.auto = {day: 'now/d', week: 'now/w'};
    }

    HighlightsConfigController.$inject = ['$scope', 'highlightsService', 'desks', 'api', 'gettext', 'notify', 'modal'];
    function HighlightsConfigController($scope, highlightsService, desks, api, gettext, notify, modal) {

        highlightsService.get().then(function(items) {
            $scope.configurations = items;
        });

        $scope.configEdit = {};
        $scope.modalActive = false;
        $scope.limits = 45;

        var _config;

        $scope.edit = function(config) {
            $scope.message = null;
            $scope.modalActive = true;
            $scope.configEdit = _.create(config);
            $scope.assignedDesks = deskList(config.desks);
            $scope.editingGroup = null;
            $scope.selectedGroup = null;
            _config = config;
            if (!$scope.configEdit.auto_insert) {
                $scope.configEdit.auto_insert = 'now/d'; // today
            }
            if (!$scope.configEdit.groups) {
                $scope.configEdit.groups = [];
            }
        };

        $scope.cancel = function() {
            $scope.modalActive = false;
        };

        $scope.save = function() {
            var _new = !_config._id;
            $scope.configEdit.desks = assignedDesks();
            if ($scope.configEdit.groups.length === 0) {
                $scope.configEdit.groups = ['main'];
            } else {
                $scope.configEdit.groups = $scope.configEdit.groups.slice(0);
            }
            api.highlights.save(_config, $scope.configEdit)
            .then(function(item) {
                $scope.message = null;
                if (_new) {
                    $scope.configurations._items.unshift(item);
                }
                highlightsService.clearCache();
                $scope.modalActive = false;
            }, function(response) {
                errorMessage(response);
            });

            function errorMessage(response) {
                if (response.data && response.data._issues && response.data._issues.name && response.data._issues.name.unique) {
                    $scope.message = gettext(
                        'Highlight configuration with the same name already exists.'
                    );
                } else {
                    $scope.message = gettext('There was a problem while saving highlights configuration');
                }
            }
        };

        $scope.remove = function(config) {
            modal.confirm(gettext('Are you sure you want to delete configuration?'))
            .then(function() {
                api.highlights.remove(config).then(function() {
                    _.remove($scope.configurations._items, config);
                    notify.success(gettext('Configuration deleted.'), 3000);
                });
            });
        };

        $scope.getHourVal = function(hour) {
            return 'now-' + hour + 'h';
        };

        function deskList(arr) {
            return _.map($scope.desks, function(d) {
                return {
                    _id: d._id,
                    name: d.name,
                    included: isIncluded(arr, d._id)
                };
            });
        }

        function isIncluded(arr, id) {
            return _.findIndex(arr, function(c) { return c === id; }) > -1;
        }

        function assignedDesks() {
            return _.map(_.filter($scope.assignedDesks, {included: true}),
                function(desk) {
                    return desk._id;
                });
        }

        $scope.isActiveGroup = function(group) {
            return $scope.editingGroup && $scope.editingGroup.id &&
                $scope.configEdit.groups[$scope.editingGroup.id - 1] === group;
        };

        $scope.editGroup = function(group) {
            if (group !== '') {
                $scope.editingGroup = {'name': group, 'id': $scope.configEdit.groups.indexOf(group) + 1};
            } else {
                $scope.editingGroup = {'name': '', 'id': 0};
            }
        };

        $scope.removeGroup = function(group) {
            $scope.configEdit.groups.splice($scope.configEdit.groups.indexOf(group), 1);
        };

        $scope.cancelGroup = function() {
            $scope.editingGroup = null;
            $scope.selectedGroup = null;
        };

        $scope.saveGroup = function() {
            if ($scope.editingGroup.id === 0) {
                $scope.configEdit.groups.push($scope.editingGroup.name);
            } else if ($scope.editingGroup.id > 0) {
                $scope.configEdit.groups[$scope.editingGroup.id - 1] = $scope.editingGroup.name;
            }
            $scope.cancelGroup();
        };

        $scope.handleGroupEdit = function($event) {
            $scope._errorLimits = null;
            if ($scope.editingGroup && $scope.editingGroup.name) {
                $scope._errorLimits = $scope.editingGroup.name.length > $scope.limits ? true : null;
            }
        };
    }

    var app = angular.module('superdesk.highlights', [
        'superdesk.desks',
        'superdesk.packaging',
        'superdesk.activity',
        'superdesk.api'
    ]);

    app
    .service('highlightsService', HighlightsService)
    .directive('sdMarkHighlightsDropdown', MarkHighlightsDropdownDirective)
    .directive('sdMultiMarkHighlightsDropdown', MultiMarkHighlightsDropdownDirective)
    .directive('sdPackageHighlightsDropdown', PackageHighlightsDropdownDirective)
    .directive('sdHighlightsTitle', HighlightsTitleDirective)
    .directive('sdSearchHighlights', SearchHighlightsDirective)
    .directive('sdHighlightsConfig', function() {
        return {
            controller: HighlightsConfigController
        };
    })
    .directive('sdHighlightsConfigModal', function() {
        return {
            require: '^sdHighlightsConfig',
            templateUrl: 'scripts/superdesk-highlights/views/highlights_config_modal.html',
            link: function(scope, elem, attrs, ctrl) {

            }
        };
    })
    .config(['superdeskProvider', function(superdesk) {
        superdesk
        .activity('mark.item', {
            label: gettext('Mark item'),
            priority: 30,
            icon: 'list-plus',
            dropdown: true,
            templateUrl: 'scripts/superdesk-highlights/views/mark_highlights_dropdown.html',
            filters: [
                {action: 'list', type: 'archive'}
            ],
            group: 'highlights',
            additionalCondition:['authoring', 'item', function(authoring, item) {
                return authoring.itemActions(item).mark_item;
            }]
        })
        .activity('/settings/highlights', {
            label: gettext('Highlights'),
            controller: HighlightsSettingsController,
            templateUrl: 'scripts/superdesk-highlights/views/settings.html',
            category: superdesk.MENU_SETTINGS,
            priority: -800,
            privileges: {highlights: 1}
        });
    }])
    .config(['apiProvider', function(apiProvider) {
        apiProvider.api('highlights', {
            type: 'http',
            backend: {rel: 'highlights'}
        });
        apiProvider.api('markForHighlights', {
            type: 'http',
            backend: {rel: 'marked_for_highlights'}
        });
        apiProvider.api('generate_highlights', {
            type: 'http',
            backend: {rel: 'generate_highlights'}
        });
    }]);

    return app;
})();
