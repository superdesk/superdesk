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

        /**
         * Get single highlight by its id
         *
         * @param {string} _id
         * @return {Promise}
         */
        service.find = function(_id) {
            return api.find('highlights', _id);
        };

        return service;
    }

    MarkHighlightsDropdownDirective.$inject = ['desks', 'highlightsService', '$timeout'];
    function MarkHighlightsDropdownDirective(desks, highlightsService, $timeout) {
        return {
            templateUrl: 'scripts/superdesk-highlights/views/mark_highlights_dropdown_directive.html',
            link: function(scope) {

                scope.markItem = function(highlight) {
                    scope.item.multiSelect = false;
                    highlightsService.markItem(highlight._id, scope.item._id);
                };

                scope.isMarked = function(highlight) {
                    return scope.item && scope.item.highlights && scope.item.highlights.indexOf(highlight._id) >= 0;
                };

                highlightsService.get(desks.getCurrentDeskId()).then(function(result) {
                    scope.highlights = result._items;
                    $timeout(function () {
                        angular.element('.more-activity-menu.open .dropdown-noarrow')
                                .find('button:not([disabled])')[0].focus();
                    });
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
                        item.multiSelect = true;
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
                item: '=item'
            },
            templateUrl: 'scripts/superdesk-highlights/views/highlights_title_directive.html',
            // todo(petr): refactor to use popover-template once angular-bootstrap 0.13 is out
            link: function(scope, elem) {

                /*
                 * Toggle 'open' class on dropdown menu element
                 * @param {string} isOpen
                 */
                scope.toggleClass = function (isOpen) {
                    scope.open = isOpen;
                };

                scope.$watch('item.highlights', function(items) {
                    if (items) {
                        highlightsService.get().then(function(result) {
                            scope.highlights = _.filter(result._items, function(highlight) {
                                return items.indexOf(highlight._id) >= 0;
                            });
                        });
                    }
                });

                elem.on({
                    click: function (e) {
                        e.preventDefault();
                        e.stopPropagation();
                    },
                    mouseenter: function () {
                        $(this).find('.highlights-list').not('.open').children('.dropdown-toggle').click();
                    }
                });

                /*
                 * Removing highlight from an item
                 * @param {string} highlight
                 */
                scope.unmarkHighlight = function (highlight) {
                    highlightsService.markItem(highlight, scope.item._id).then(function() {
                        scope.item.highlights = _.without(scope.item.highlights, highlight);
                    });
                };
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

    PackageHighlightsDropdownDirective.$inject = ['desks', 'highlightsService', '$location', '$route'];
    function PackageHighlightsDropdownDirective(desks, highlightsService, $location, $route) {
        return {
            scope: true,
            templateUrl: 'scripts/superdesk-highlights/views/package_highlights_dropdown_directive.html',
            link: function(scope) {
                scope.$watch(function() {
                    return desks.active;
                }, function(active) {
                    scope.selected = active;
                    highlightsService.get(active.desk).then(function(result) {
                        scope.highlights = result._items;
                        scope.hasHighlights = _.size(scope.highlights) > 0;
                    });
                });

                scope.listHighlight = function(highlight) {
                    $location.url('workspace/highlights?highlight=' + highlight._id);
                    $route.reload();
                };
            }
        };
    }

    HighlightLabelDirective.$inject = ['desks', 'highlightsService'];
    function HighlightLabelDirective(desks, highlightsService) {
        return {
            scope: {highlight_id: '=highlight'},
            template: '<span translate>{{ highlightItem.name }}</span>',
            link: function(scope) {
                highlightsService.get(desks.getCurrentDeskId()).then(function(result) {
                    scope.highlightItem =  _.find(result._items, {_id: scope.highlight_id});
                });
            }
        };
    }

    CreateHighlightsButtonDirective.$inject = ['highlightsService', 'authoringWorkspace'];
    function CreateHighlightsButtonDirective(highlightsService, authoringWorkspace) {
        return {
            scope: {highlight_id: '=highlight'},
            templateUrl: 'scripts/superdesk-highlights/views/create_highlights_button_directive.html',
            link: function(scope) {
                /**
                 * Create new highlight package for current highlight and start editing it
                 */
                scope.createHighlight = function() {
                    highlightsService.find(scope.highlight_id)
                        .then(highlightsService.createEmptyHighlight)
                        .then(authoringWorkspace.edit);
                };
            }
        };
    }

    HighlightsSettingsController.$inject = ['$scope', 'api', 'desks'];
    function HighlightsSettingsController($scope, api, desks) {
        desks.initialize().then(function() {
            $scope.desks = desks.deskLookup;
        });

        api.query('content_templates', {'template_type': 'highlights'}).then(function(result) {
            $scope.templates = result._items || [];
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
    .directive('sdCreateHighlightsButton', CreateHighlightsButtonDirective)
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
    .directive('sdHighlightLabel', HighlightLabelDirective)
    .config(['superdeskProvider', function(superdesk) {
        superdesk
        .activity('mark.item', {
            label: gettext('Mark for highlight'),
            priority: 30,
            icon: 'list-plus',
            dropdown: true,
            keyboardShortcut: 'ctrl+shift+d',
            templateUrl: 'scripts/superdesk-highlights/views/mark_highlights_dropdown.html',
            filters: [
                {action: 'list', type: 'archive'}
            ],
            additionalCondition:['authoring', 'item', function(authoring, item) {
                return authoring.itemActions(item).mark_item;
            }],
            group: 'packaging'
        })
        .activity('/settings/highlights', {
            label: gettext('Highlights'),
            controller: HighlightsSettingsController,
            templateUrl: 'scripts/superdesk-highlights/views/settings.html',
            category: superdesk.MENU_SETTINGS,
            priority: -800,
            privileges: {highlights: 1}
        }).
        activity('/workspace/highlights', {
            label: gettext('Highlights View'),
            priority: 100,
            templateUrl: 'scripts/superdesk-monitoring/views/highlights-view.html',
            topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
            sideTemplateUrl: 'scripts/superdesk-workspace/views/workspace-sidenav.html'
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
