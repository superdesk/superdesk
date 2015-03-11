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
        rss: {
            label: 'RSS',
            templateUrl: 'scripts/superdesk-ingest/views/settings/rssConfig.html'
        },
        afp: {
            label: 'AFP',
            templateUrl: 'scripts/superdesk-ingest/views/settings/afpConfig.html'
        },
        ftp: {
            label: 'FTP',
            templateUrl: 'scripts/superdesk-ingest/views/settings/ftp-config.html'
        },
        teletype: {
            label: 'Teletype',
            templateUrl: 'scripts/superdesk-ingest/views/settings/teletypeConfig.html'
        },
        email: {
            label: 'Email',
            templateUrl: 'scripts/superdesk-ingest/views/settings/emailConfig.html'
        },
        dpa: {
            label: 'DPA',
            templateUrl: 'scripts/superdesk-ingest/views/settings/aapConfig.html'
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

    SubjectService.$inject = ['api'];
    function SubjectService(api) {
        var service = {
            rawSubjects: null,
            qcodeLookup: {},
            subjects: [],
            fetched: null,
            fetchSubjects: function() {
                var self = this;

                return api.get('/subjectcodes')
                .then(function(result) {
                    self.rawSubjects = result;
                });
            },
            process: function() {
                var self = this;

                _.each(this.rawSubjects._items, function(item) {
                    self.qcodeLookup[item.qcode] = item;
                });
                _.each(this.rawSubjects._items, function(item) {
                    self.subjects.push({qcode: item.qcode, name: item.name, path: self.getPath(item)});
                });

                return this.subjects;
            },
            getPath: function(item) {
                var path = '';
                if (item.parent) {
                    path = this.getPath(this.qcodeLookup[item.parent]) + this.qcodeLookup[item.parent].name + ' / ';
                }
                return path;
            },
            initialize: function() {
                if (!this.fetched) {
                    this.fetched = this.fetchSubjects()
                        .then(angular.bind(this, this.process));
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
        $scope.loading = false;
        $scope.repo = {
            ingest: true,
            archive: false
        };
        $scope.api = api.ingest;
        $rootScope.currentModule = 'ingest';

        this.fetchItems = function(criteria) {
            $scope.loading = true;
            api.ingest.query(criteria).then(function(items) {
                $scope.items = items;
            })
            ['finally'](function() {
                $scope.loading = false;
            });
        };

        var oldQuery = _.omit($location.search(), '_id');
        var update = angular.bind(this, function searchUpdated() {
            var newquery = _.omit($location.search(), '_id');
            if (!_.isEqual(_.omit(newquery, 'page'), _.omit(oldQuery, 'page'))) {
                $location.search('page', null);
            }
            var query = this.getQuery($location.search());
            this.fetchItems({source: query});
            oldQuery = newquery;
        });

        $scope.$on('ingest:update', update);
        $scope.$on('item:fetch', update);
        $scope.$watchCollection(function getSearchWithoutId() {
            return _.omit($location.search(), '_id');
        }, update);
    }

    IngestSettingsController.$inject = ['$scope', 'privileges'];
    function IngestSettingsController($scope, privileges) {
        var user_privileges = privileges.privileges;

        $scope.showIngest   = Boolean(user_privileges.ingest_providers);
        $scope.showRuleset  = Boolean(user_privileges.rule_sets);
        $scope.showRouting  = Boolean(user_privileges.routing_rules);
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
                        .value(function(d) { return d.doc_count; })
                        .sort(sort ? function(a, b) { return d3.ascending(a[sort], b[sort]); } : null);

                    var svg = d3.select(appendTarget).append('svg')
                        .attr('width', width)
                        .attr('height', height)
                        .append('g')
                        .attr('transform', 'translate(' + width / 2 + ',' + height / 2 + ')');

                    scope.$watchGroup(['terms', 'colors'], function renderData(newData) {
                        if (newData[0] != null) {

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
                                .style('fill', function(d) { return colorScale(d.data.key); });

                            g.append('text')
                                .attr('transform', function(d) { return 'translate(' + arc.centroid(d) + ')'; })
                                .style('text-anchor', 'middle')
                                .style('fill', colorScheme.text)
                                .text(function(d) { return d.data.key; });
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

                api('routing_schemes').query().then(function(result) {
                    $scope.routingScheme = result._items;
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
                    $scope.provider.notifications = $scope.origProvider.notifications;
                };

                $scope.cancel = function() {
                    $scope.origProvider = null;
                    $scope.provider = null;
                };

                $scope.setConfig = function(provider) {
                    $scope.provider.config = provider.config;
                };

                /**
                * Updates provider configuration object. It also clears the
                * username and password fields, if authentication is not
                * needed for an RSS source.
                *
                * @method setRssConfig
                * @param {Object} provider ingest provider instance
                */
                $scope.setRssConfig = function(provider) {
                    if (!provider.config.auth_required) {
                        provider.config.username = null;
                        provider.config.password = null;
                    }
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

    IngestRoutingContent.$inject = ['api', 'gettext', 'notify', 'modal'];
    function IngestRoutingContent(api, gettext, notify, modal) {
        return {
            templateUrl: 'scripts/superdesk-ingest/views/settings/ingest-routing-content.html',
            link: function(scope) {
                var _orig = null;
                scope.editScheme = null;
                scope.rule = null;
                scope.ruleIndex = null;
                scope.schemes = [];

                api('routing_schemes')
                .query()
                .then(function(result) {
                    scope.schemes = result._items;
                });

                function confirm() {
                    return modal.confirm(gettext('Are you sure you want to delete scheme?'));
                }

                scope.edit = function(scheme) {
                    scope.editScheme = _.clone(scheme);
                    scope.editScheme.rules = scope.editScheme.rules || [];
                    _orig = scheme;
                };

                scope.save = function() {
                    if (scope.rule) {
                        if (scope.ruleIndex === -1) {
                            scope.editScheme.rules.push(scope.rule);
                        } else {
                            scope.editScheme.rules[scope.ruleIndex] = scope.rule;
                        }
                    }
                    var _new = scope.editScheme._id ? false : true;
                    api('routing_schemes').save(_orig, scope.editScheme)
                    .then(function() {
                        if (_new) {
                            scope.schemes.push(_orig);
                        }
                        notify.success(gettext('Routing scheme saved.'));
                        scope.cancel();
                    }, function(response) {
                        notify.error(gettext('I\'m sorry but there was an error when saving the routing scheme.'));
                    });
                };

                scope.cancel = function() {
                    scope.editScheme = null;
                    scope.rule = null;
                };

                scope.remove = function(scheme) {
                    confirm().then(function() {
                        api('routing_schemes').remove(scheme)
                        .then(function(result) {
                            _.remove(scope.schemes, scheme);
                        }, function(response) {
                            if (response.status === 400) {
                                notify.error(gettext('Routing scheme is applied to channel(s). It cannot be deleted.'));
                            } else {
                                notify.error(gettext('There is an error. Routing scheme cannot be deleted.'));
                            }
                        });
                    });
                };

                scope.removeRule = function(rule) {
                    _.remove(scope.editScheme.rules, rule);
                };

                scope.addRule = function() {
                    var rule = {
                        name: null,
                        filter: {
                            type: [],
                            headline: '',
                            slugline: '',
                            body: '',
                            subject: [],
                            category: [],
                            genre: []
                        },
                        actions: {
                            fetch: [],
                            publish: [],
                            exit: false
                        },
                        schedule: {
                            day_of_week: ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'],
                            hour_of_day_from: '0000',
                            hour_of_day_to: '2355'
                        }
                    };
                    scope.editRule(rule);
                };

                scope.editRule = function(rule) {
                    scope.ruleIndex = _.findIndex(scope.editScheme.rules, rule);
                    scope.rule = _.clone(rule);
                };

                scope.reorder = function(start, end) {
                    scope.editScheme.rules.splice(end, 0, scope.editScheme.rules.splice(start, 1)[0]);
                };
            }
        };
    }

    var typeLookup = {
        text: 'Text',
        preformatted: 'Preformatted text',
        picture: 'Picture',
        audio: 'Audio',
        video: 'Video',
        composite: 'Package'
    };

    var dayLookup = {
        MON: 'Monday',
        TUE: 'Tuesday',
        WED: 'Wednesday',
        THU: 'Thursday',
        FRI: 'Friday',
        SAT: 'Saturday',
        SUN: 'Sunday'
    };

    IngestRoutingGeneral.$inject = ['desks'];
    function IngestRoutingGeneral(desks) {
        return {
            scope: {rule: '='},
            templateUrl: 'scripts/superdesk-ingest/views/settings/ingest-routing-general.html',
            link: function(scope) {
                scope.typeLookup = typeLookup;
                scope.dayLookup = dayLookup;
                desks.initialize()
                .then(function() {
                    scope.deskLookup = desks.deskLookup;
                    scope.stageLookup = desks.stageLookup;
                });
            }
        };
    }

    IngestRoutingFilter.$inject = ['api', 'subjectService'];
    function IngestRoutingFilter(api, subjectService) {
        return {
            scope: {rule: '='},
            templateUrl: 'scripts/superdesk-ingest/views/settings/ingest-routing-filter.html',
            link: function(scope) {
                scope.typeList = [
                    'text',
                    'preformatted',
                    'picture',
                    'audio',
                    'video',
                    'composite'
                ];
                scope.typeLookup = typeLookup;
                scope.subjects = [];
                scope.subjectTerm = '';
                scope.filteredSubjects = [];

                scope.categories = [];
                scope.categoryTerm = '';
                scope.filteredCategories = [];

                scope.genres = [];
                scope.genreTerm = '';
                scope.filteredGenres = [];

                subjectService
                .initialize()
                .then(function(subjects) {
                    scope.subjects = subjects;
                });

                api.get('vocabularies')
                .then(function(result) {
                    scope.categories = _.find(result._items, {_id: 'categories'}).items;
                    scope.genres = _.find(result._items, {_id: 'genre'}).items;
                });

                scope.isTypeChecked = function(rule, type) {
                    return rule.filter.type.indexOf(type) !== -1;
                };

                scope.toggleType = function(rule, type) {
                    if (scope.isTypeChecked(rule, type)) {
                        rule.filter.type = _.without(rule.filter.type, type);
                    } else {
                        rule.filter.type.push(type);
                    }
                };

                scope.removeSubject = function(subject) {
                    _.remove(scope.rule.filter.subject, function(s) {
                        return s.qcode === subject.qcode;
                    });
                };

                scope.selectSubject = function(item) {
                    scope.rule.filter.subject.push({qcode: item.qcode, name: item.name});
                    scope.subjectTerm = '';
                };

                scope.searchSubjects = function(term) {
                    var regex = new RegExp(term, 'i');
                    scope.filteredSubjects = _.filter(scope.subjects, function(subject) {
                        return (
                            regex.test(subject.name) &&
                            _.findIndex(scope.rule.filter.subject, {qcode: subject.qcode}) === -1
                        );
                    });
                };

                scope.removeCategory = function(category) {
                    _.remove(scope.rule.filter.category, function(c) {
                        return c.qcode === category.qcode;
                    });
                };

                scope.selectCategory = function(item) {
                    scope.rule.filter.category.push({qcode: item.value, name: item.name});
                    scope.categoryTerm = '';
                };

                scope.searchCategories = function(term) {
                    var regex = new RegExp(term, 'i');
                    scope.filteredCategories = _.filter(scope.categories, function(category) {
                        return (
                            regex.test(category.name) &&
                            _.findIndex(scope.rule.filter.category, {qcode: category.value}) === -1 &&
                            category.is_active === true
                        );
                    });
                };

                scope.removeGenre = function(genre) {
                    _.remove(scope.rule.filter.genre, function(g) {
                        return g === genre.value;
                    });
                };

                scope.selectGenre = function(item) {
                    scope.rule.filter.genre.push(item.value);
                    scope.genreTerm = '';
                };

                scope.searchGenres = function(term) {
                    var regex = new RegExp(term, 'i');
                    scope.filteredGenres = _.filter(scope.genres, function(genre) {
                        return (
                            regex.test(genre.name) &&
                            scope.rule.filter.genre.indexOf(genre.value) === -1 &&
                            genre.is_active === true
                        );
                    });
                };
            }
        };
    }

    IngestRoutingAction.$inject = ['desks'];
    function IngestRoutingAction(desks) {
        return {
            scope: {rule: '='},
            templateUrl: 'scripts/superdesk-ingest/views/settings/ingest-routing-action.html',
            link: function(scope) {
                scope.newFetch = {};
                scope.newPublish = {};
                scope.deskLookup = {};
                scope.stageLookup = {};

                desks.initialize()
                .then(function() {
                    scope.deskLookup = desks.deskLookup;
                    scope.stageLookup = desks.stageLookup;
                });

                scope.addFetch = function() {
                    if (scope.newFetch.desk && scope.newFetch.stage) {
                        scope.rule.actions.fetch.push(scope.newFetch);
                        scope.newFetch = {};
                    }
                };

                scope.removeFetch = function(fetchAction) {
                    _.remove(scope.rule.actions.fetch, function(f) {
                        return f === fetchAction;
                    });
                };

                scope.addPublish = function() {
                    if (scope.newPublish.desk && scope.newPublish.stage) {
                        scope.rule.actions.publish.push(scope.newPublish);
                        scope.newPublish = {};
                    }
                };

                scope.removePublish = function(publishAction) {
                    _.remove(scope.rule.actions.publish, function(p) {
                        return p === publishAction;
                    });
                };
            }
        };
    }

    IngestRoutingSchedule.$inject = [];
    function IngestRoutingSchedule() {
        return {
            scope: {rule: '='},
            templateUrl: 'scripts/superdesk-ingest/views/settings/ingest-routing-schedule.html',
            link: function(scope) {
                scope.dayList = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];
                scope.dayLookup = dayLookup;

                scope.isDayChecked = function(rule, day) {
                    return rule.schedule.day_of_week.indexOf(day) !== -1;
                };

                scope.toggleDay = function(rule, day) {
                    if (scope.isDayChecked(rule, day)) {
                        rule.schedule.day_of_week = _.without(rule.schedule.day_of_week, day);
                    } else {
                        rule.schedule.day_of_week.push(day);
                    }
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

    function InsertFilter() {
        return function(input, location, addition) {
            location = location || input.length;
            addition = addition || '';

            return input.substr(0, location) + addition + input.substr(location);
        };
    }

    app
        .service('ingestSources', IngestProviderService)
        .factory('subjectService', SubjectService)
        .directive('sdIngestSourcesContent', IngestSourcesContent)
        .directive('sdIngestRulesContent', IngestRulesContent)
        .directive('sdIngestRoutingContent', IngestRoutingContent)
        .directive('sdIngestRoutingGeneral', IngestRoutingGeneral)
        .directive('sdIngestRoutingFilter', IngestRoutingFilter)
        .directive('sdIngestRoutingAction', IngestRoutingAction)
        .directive('sdIngestRoutingSchedule', IngestRoutingSchedule)
        .directive('sdPieChartDashboard', PieChartDashboardDirective)
        .directive('sdSortrules', SortRulesDirectives)
        .filter('insert', InsertFilter);

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
                monitor: true,
                controller: ['api', 'data', 'desks', function(api, data, desks) {
                    api.archiveIngest.create({
                        guid: data.item.guid,
                        desk: desks.getCurrentDeskId()
                    })
                    .then(function(archiveItem) {
                        data.item.task_id = archiveItem.task_id;
                        data.item.archived = archiveItem._created;
                    }, function(response) {
                        data.item.error = response;
                    })
                    ['finally'](function() {
                        data.item.actioning.archive = false;
                    });
                }],
                filters: [
                    {action: 'list', type: 'ingest'}
                ],
                action: 'fetch_as_from_ingest',
                key: 'f'
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
