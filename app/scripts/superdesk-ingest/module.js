define([
    'angular',
    'd3',
    'superdesk-archive/controllers/baseList',
    './ingest-widget/ingest',
    './ingest-stats-widget/stats'
], function(angular, d3, BaseListController) {
    'use strict';

    var app = angular.module('superdesk.ingest', [
        'superdesk.search',
        'superdesk.dashboard',
        'superdesk.widgets.ingest',
        'superdesk.widgets.ingeststats'
    ]);

    app.value('providerTypes', {
        aap: {
            label: 'AAP',
            templateUrl: 'scripts/superdesk-ingest/views/settings/aapConfig.html'
        },
        reuters: {
            label: 'Reuters',
            templateUrl: 'scripts/superdesk-ingest/views/settings/reutersConfig.html'
        },
        afp: {
            label: 'AFP',
            templateUrl: 'scripts/superdesk-ingest/views/settings/afpConfig.html'
        },
        ftp: {
            label: 'FTP',
            templateUrl: 'scripts/superdesk-ingest/views/settings/ftp-config.html'
        }
    });

    IngestProviderService.$inject = ['api', '$q'];
    function IngestProviderService(api, $q) {

        var service = {
            providers: null,
            providersLookup: {},
            fetched: null,
            fetchProviders: function() {
                var self = this;
                return api.ingestProviders.query().then(function(result) {
                    self.providers = result._items;
                });
            },
            generateLookup: function() {
                var self = this;

                this.providersLookup = _.indexBy(self.providers, '_id');

                return $q.when();
            },
            initialize: function() {
                if (!this.fetched) {

                    this.fetched = this.fetchProviders()
                        .then(angular.bind(this, this.generateLookup));
                }

                return this.fetched;
            }
        };
        return service;
    }

    IngestListController.$inject = ['$scope', '$injector', '$location', 'api', '$rootScope'];
    function IngestListController($scope, $injector, $location, api, $rootScope) {
        $injector.invoke(BaseListController, this, {$scope: $scope});

        $scope.type = 'ingest';
        $scope.repo = {
            ingest: true,
            archive: false
        };
        $scope.api = api.ingest;
        $rootScope.currentModule = 'ingest';

        this.fetchItems = function(criteria) {
            api.ingest.query(criteria).then(function(items) {
                $scope.items = items;
            });
        };

        var update = angular.bind(this, function searchUpdated() {
            var query = this.getQuery($location.search());
            this.fetchItems({source: query});
        });

        $scope.$on('ingest:update', update);
        $scope.$watchCollection(function getSearchWithoutId() {
            return _.omit($location.search(), '_id');
        }, update);
    }

    IngestSettingsController.$inject = ['$scope'];
    function IngestSettingsController($scope) {

    }

    PieChartDashboardDirective.$inject = ['colorSchemes'];
    function PieChartDashboardDirective(colorSchemes) {
        return {
            replace: true,
            scope: {
                terms: '=',
                theme: '@',
                colors: '='
            },
            link: function(scope, element, attrs) {

                var appendTarget = element[0];
                var horizBlocks = attrs.x ? parseInt(attrs.x, 10) : 1;
                var vertBlocks  = attrs.y ? parseInt(attrs.y, 10) : 1;

                var graphSettings = {       //thightly depends on CSS
                    blockWidth: 300,
                    blockHeight: 197,
                    mergeSpaceLeft: 60,     //30 + 2 + 20
                    mergeSpaceBottom: 99    //30 + 2 + 20 + 47
                };

                var width = graphSettings.blockWidth * horizBlocks + graphSettings.mergeSpaceLeft * (horizBlocks - 1),
                    height = graphSettings.blockHeight * vertBlocks + graphSettings.mergeSpaceBottom * (vertBlocks - 1),
                    radius = Math.min(width, height) / 2;

                colorSchemes.get(function(colorsData) {

                    var colorScheme = colorsData.schemes[0];

                    var arc = d3.svg.arc()
                        .outerRadius(radius)
                        .innerRadius(radius * 8 / 13 / 2);

                    var sort = attrs.sort || null;
                    var pie = d3.layout.pie()
                        .value(function(d) { return d.count; })
                        .sort(sort ? function(a, b) { return d3.ascending(a[sort], b[sort]); } : null);

                    var svg = d3.select(appendTarget).append('svg')
                        .attr('width', width)
                        .attr('height', height)
                        .append('g')
                        .attr('transform', 'translate(' + width / 2 + ',' + height / 2 + ')');

                    scope.$watchCollection('[ terms, colors]', function(newData) {

                        if (newData[0] !== undefined) {

                            if (newData[1] !== null) {
                                colorScheme = colorsData.schemes[_.findKey(colorsData.schemes, {name: newData[1]})];
                            }

                            var colorScale = d3.scale.ordinal()
                                    .range(colorScheme.charts);

                            svg.selectAll('.arc').remove();

                            var g = svg.selectAll('.arc')
                                .data(pie(newData[0]))
                                .enter().append('g')
                                .attr('class', 'arc');

                            g.append('path')
                                .attr('d', arc)
                                .style('fill', function(d) { return colorScale(d.data.term); });

                            g.append('text')
                                .attr('transform', function(d) { return 'translate(' + arc.centroid(d) + ')'; })
                                .style('text-anchor', 'middle')
                                .style('fill', colorScheme.text)
                                .text(function(d) { return d.data.term; });
                        }

                    });
                });
            }
        };
    }

    IngestSourcesContent.$inject = ['providerTypes', 'gettext', 'notify', 'api', '$location'];
    function IngestSourcesContent(providerTypes, gettext, notify, api, $location) {
        return {
            templateUrl: 'scripts/superdesk-ingest/views/settings/ingest-sources-content.html',
            link: function($scope) {

                var DEFAULT_SCHEDULE = {minutes: 5, seconds: 0};

                $scope.provider = null;
                $scope.origProvider = null;

                $scope.types = providerTypes;
                $scope.minutes = [0, 1, 2, 3, 4, 5, 8, 10, 15, 30, 45];
                $scope.seconds = [0, 5, 10, 15, 30, 45];

                fetchProviders();

                function fetchProviders() {
                    return api.ingestProviders.query({max_results: 100})
                        .then(function(result) {
                            $scope.providers = result;
                        });
                }

                api('rule_sets').query().then(function(result) {
                    $scope.rulesets = result._items;
                });

                $scope.remove = function(provider) {
                    api.ingestProviders.remove(provider)
                    .then(function() {
                        notify.success(gettext('Provider deleted.'));
                    }).then(fetchProviders);
                };

                $scope.edit = function(provider) {
                    $scope.origProvider = provider || {};
                    $scope.provider = _.create($scope.origProvider);
                    $scope.provider.update_schedule = $scope.origProvider.update_schedule || DEFAULT_SCHEDULE;
                    $scope.offProvider = provider.is_closed;
                };

                $scope.cancel = function() {
                    $scope.origProvider = null;
                    $scope.provider = null;
                };

                $scope.setConfig = function(provider) {
                    $scope.provider.config = provider.config;
                };

                $scope.save = function() {
                    api.ingestProviders.save($scope.origProvider, $scope.provider)
                    .then(function() {
                        notify.success(gettext('Provider saved!'));
                        $scope.cancel();
                    }).then(fetchProviders);
                };

                $scope.gotoIngest = function(source) {
                    $location.path('/workspace/ingest').search('source', angular.toJson([source]));
                };
            }
        };
    }

    IngestRulesContent.$inject = ['api', 'gettext', 'notify', 'modal'];
    function IngestRulesContent(api, gettext, notify, modal) {
        return {
            templateUrl: 'scripts/superdesk-ingest/views/settings/ingest-rules-content.html',
            link: function(scope) {

                var _orig = null;
                scope.editRuleset = null;

                api('rule_sets').query().then(function(result) {
                    scope.rulesets = result._items;
                });

               scope.edit = function(ruleset) {
                    scope.editRuleset = _.create(ruleset);
                    scope.editRuleset.rules = ruleset.rules || [];
                    _orig = ruleset;
                };

                scope.save = function(ruleset) {
                    var _new = ruleset._id ? false : true;
                    api('rule_sets').save(_orig, ruleset)
                    .then(function() {
                        if (_new) {
                            scope.rulesets.push(_orig);
                        }
                        notify.success(gettext('Rule set saved.'));
                        scope.cancel();
                    }, function(response) {
                        notify.error(gettext('I\'m sorry but there was an error when saving the rule set.'));
                    });
                };

                scope.cancel = function() {
                    scope.editRuleset = null;
                };

                scope.remove = function(ruleset) {
                    confirm().then(function() {
                        api('rule_sets').remove(ruleset)
                        .then(function(result) {
                            _.remove(scope.rulesets, ruleset);
                        }, function(response) {
                            if (response.status === 400) {
                                notify.error(gettext('Rule set is applied to channel(s). It cannot be deleted.'));
                            } else {
                                notify.error(gettext('There is an error. Rule set cannot be deleted.'));
                            }
                        });
                    });
                };

                function confirm() {
                    return modal.confirm(gettext('Are you sure you want to delete rule set?'));
                }

                scope.removeRule = function(rule) {
                    _.remove(scope.editRuleset.rules, rule);
                };

                scope.addRule = function() {
                    if (!scope.editRuleset.rules) {
                        scope.editRuleset.rules = [];
                    }
                    scope.editRuleset.rules.push({old: null, 'new': null});
                };

                scope.reorder = function(start, end) {
                    scope.editRuleset.rules.splice(end, 0, scope.editRuleset.rules.splice(start, 1)[0]);
                };
            }
        };
    }

    function SortRulesDirectives() {
        return {
            link:function(scope, element) {
                element.sortable({
                    items: 'li',
                    connectWith: '.rule-list',
                    cursor: 'move',
                    start: function(event, ui) {
                        ui.item.data('start', ui.item.index());
                    },
                    stop: function(event, ui) {
                        var start = ui.item.data('start'), end = ui.item.index();
                        scope.reorder(start, end);
                        scope.$apply();
                    }
                });
            }
        };
    }

    app
        .service('ingestSources', IngestProviderService)
        .directive('sdIngestSourcesContent', IngestSourcesContent)
        .directive('sdIngestRulesContent', IngestRulesContent)
        .directive('sdPieChartDashboard', PieChartDashboardDirective)
        .directive('sdSortrules', SortRulesDirectives);

    app.config(['superdeskProvider', function(superdesk) {
        superdesk
            .activity('/workspace/ingest', {
                label: gettext('Workspace'),
                priority: 100,
                controller: IngestListController,
                templateUrl: 'scripts/superdesk-archive/views/list.html',
                category: '/workspace',
                topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
                privileges: {ingest: 1}
            })
            .activity('/settings/ingest', {
                label: gettext('Ingest'),
                templateUrl: 'scripts/superdesk-ingest/views/settings/settings.html',
                controller: IngestSettingsController,
                category: superdesk.MENU_SETTINGS,
                privileges: {ingest_providers: 1}
            })
            .activity('archive', {
                label: gettext('Fetch'),
                icon: 'archive',
                controller: ['api', 'data', 'desks', function(api, data, desks) {
                    api.archiveIngest.create({
                        guid: data.item.guid,
                        desk: desks.getCurrentDeskId()
                    })
                    .then(function(archiveItem) {
                        data.item.task_id = archiveItem.task_id;
                        data.item.created = archiveItem.created;
                    });
                }],
                filters: [
                    {action: 'list', type: 'ingest'}
                ],
                action: 'fetch_as_from_ingest'
            });
    }]);

    app.config(['apiProvider', function(apiProvider) {
        apiProvider.api('archiveIngest', {
            type: 'http',
            backend: {
                rel: 'archive_ingest'
            }
        });
        apiProvider.api('ingest', {
            type: 'http',
            backend: {
                rel: 'ingest'
            }
        });
        apiProvider.api('ingestProviders', {
            type: 'http',
            backend: {
                rel: 'ingest_providers'
            }
        });
    }]);

    return app;
});
