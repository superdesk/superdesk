define([
    'angular',
    'd3',
    'moment',
    'superdesk-archive/controllers/baseList',
    './ingest-widget/ingest',
    './ingest-stats-widget/stats'
], function(angular, d3, moment, BaseListController) {
    'use strict';

    angular.module('superdesk.ingest.send', [
        'superdesk.api',
        'superdesk.desks'
        ])
        .service('send', SendService)
        ;

    var app = angular.module('superdesk.ingest', [
        'superdesk.search',
        'superdesk.dashboard',
        'superdesk.widgets.ingest',
        'superdesk.widgets.ingeststats',
        'superdesk.ingest.send'
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
        },
        search: {
            label: 'Search provider',
            templateUrl: 'scripts/superdesk-ingest/views/settings/searchConfig.html'
        }
    });

    var PROVIDER_DASHBOARD_DEFAULTS = {
        show_log_messages: true,
        show_ingest_count: true,
        show_time: true,
        log_messages: 'error',
        show_status: true
    };

    var DEFAULT_SCHEDULE = {minutes: 5, seconds: 0};
    var DEFAULT_IDLE_TIME = {hours: 0, minutes: 0};

    function forcedExtend(dest, src) {
        _.each(PROVIDER_DASHBOARD_DEFAULTS, function(value, key) {
            if (_.has(src, key)) {
                dest[key] = src[key];
            } else {
                dest[key] = PROVIDER_DASHBOARD_DEFAULTS[key];
            }
        });
    }

    IngestProviderService.$inject = ['api', '$q', 'preferencesService'];
    function IngestProviderService(api, $q, preferencesService) {

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
            },
            fetchDashboardProviders: function() {
                var deferred = $q.defer();
                api.ingestProviders.query({max_results:500}).then(function (result) {
                    var ingest_providers = result._items;
                    preferencesService.get('dashboard:ingest').then(function(user_ingest_providers) {
                        if (!_.isArray(user_ingest_providers)) {
                            user_ingest_providers = [];
                        }

                        _.forEach(ingest_providers, function(provider) {
                            var user_provider = _.find(user_ingest_providers, function(item) {
                                return item._id === provider._id;
                            });

                            provider.dashboard_enabled = user_provider?true:false;
                            forcedExtend(provider, user_provider?user_provider:PROVIDER_DASHBOARD_DEFAULTS);
                        });

                        deferred.resolve(ingest_providers);
                    }, function (error) {
                        deferred.reject(error);
                    });
                }, function (error) {
                    deferred.reject(error);
                });

                return deferred.promise;
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

        this.fetchItem = function(id) {
            return api.ingest.getById(id);
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
                                .attr('class', 'place-label')
                                .attr('transform', function(d) { return 'translate(' + arc.centroid(d) + ')'; })
                                .style('text-anchor', 'middle')
                                .style('fill', colorScheme.text)
                                .text(function(d) { return d.data.key; });

                            arrangeLabels();
                        }

                    });
                    function arrangeLabels() {
                        var move = 1;
                        while (move > 0) {
                            move = 0;
                            svg.selectAll('.place-label')
                                    .each(rerangeLabels);
                        }
                        function rerangeLabels() {
                            /*jshint validthis: true */
                            var self = this,
                                    a = self.getBoundingClientRect();

                            svg.selectAll('.place-label')
                                    .each(function () {
                                        if (this !== self) {
                                            var b = this.getBoundingClientRect();
                                            if ((Math.abs(a.left - b.left) * 2 < (a.width + b.width)) &&
                                                    (Math.abs(a.top - b.top) * 2 < (a.height + b.height))) {

                                                var dx = (Math.max(0, a.right - b.left) +
                                                        Math.min(0, a.left - b.right)) * 0.01,
                                                        dy = (Math.max(0, a.bottom - b.top) +
                                                                Math.min(0, a.top - b.bottom)) * 0.02,
                                                        tt = d3.transform(d3.select(this).attr('transform')),
                                                        to = d3.transform(d3.select(self).attr('transform'));
                                                move += Math.abs(dx) + Math.abs(dy);
                                                to.translate = [to.translate[0] + dx, to.translate[1] + dy];
                                                tt.translate = [tt.translate[0] - dx, tt.translate[1] - dy];
                                                d3.select(this).attr('transform', 'translate(' + tt.translate + ')');
                                                d3.select(self).attr('transform', 'translate(' + to.translate + ')');
                                                a = this.getBoundingClientRect();
                                            }
                                        }
                                    });
                        }
                    }
                });
            }
        };
    }

    IngestSourcesContent.$inject = ['providerTypes', 'gettext', 'notify', 'api', '$location', 'modal'];
    function IngestSourcesContent(providerTypes, gettext, notify, api, $location, modal) {
        return {
            templateUrl: 'scripts/superdesk-ingest/views/settings/ingest-sources-content.html',
            link: function($scope) {
                $scope.provider = null;
                $scope.origProvider = null;

                $scope.types = providerTypes;
                $scope.minutes = [0, 1, 2, 3, 4, 5, 8, 10, 15, 30, 45];
                $scope.seconds = [0, 5, 10, 15, 30, 45];
                $scope.hours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24];

                // a list of all data field names in retrieved content
                // expected by the server
                // XXX: have this somewhere in config? probably better
                $scope.contentFields = [
                    'body_text', 'guid', 'published_parsed',
                    'summary', 'title', 'updated_parsed'
                ];

                // a list of data field names currently *not* selected in any
                // of the dropdown menus in the field aliases section
                $scope.fieldsNotSelected = angular.copy($scope.contentFields);

                // a list of field names aliases - used for fields in retrieved
                // content whose names differ from what the server expects
                $scope.fieldAliases = [];

                function fetchProviders() {
                    return api.ingestProviders.query({max_results: 200})
                        .then(function(result) {
                            $scope.providers = result;
                        });
                }

                function openProviderModal() {
                    var provider_id = $location.search()._id;
                    var provider;
                    if (provider_id) {
                        if ($scope.providers && $scope.providers._items) {
                            provider = _.find($scope.providers._items, function (item) {
                                return item._id === provider_id;
                            });
                        }

                        if (provider == null) {
                            api.ingestProviders.getById(provider_id).then(function (result) {
                                provider = result;
                            });
                        }

                        if (provider) {
                            $scope.edit(provider);
                        }
                    }
                }

                fetchProviders().then(function() {
                    openProviderModal();
                });

                api('rule_sets').query().then(function(result) {
                    $scope.rulesets = result._items;
                });

                api('routing_schemes').query().then(function(result) {
                    $scope.routingScheme = result._items;
                });

                $scope.fetchSourceErrors = function() {
                    if ($scope.provider && $scope.provider.type) {
                        return api('io_errors').query({'source_type': $scope.provider.type})
                            .then(function (result) {
                                $scope.provider.source_errors = result._items[0].source_errors;
                                $scope.provider.all_errors = result._items[0].all_errors;
                            });
                    }
                };

                $scope.remove = function(provider) {
                    modal.confirm(gettext('Are you sure you want to delete Ingest Source?')).then(
                        function removeIngestProviderChannel() {
                            api.ingestProviders.remove(provider)
                                .then(
                                    function () {
                                        notify.success(gettext('Ingest Source deleted.'));
                                    },
                                    function(response) {
                                        if (angular.isDefined(response.data._message)) {
                                            notify.error(response.data._message);
                                        } else {
                                            notify.error(gettext('Error: Unable to delete Ingest Source'));
                                        }
                                    }
                                ).then(fetchProviders);
                        }
                    );
                };

                $scope.edit = function(provider) {
                    var aliases;

                    $scope.origProvider = provider || {};
                    $scope.provider = _.create($scope.origProvider);
                    $scope.provider.update_schedule = $scope.origProvider.update_schedule || DEFAULT_SCHEDULE;
                    $scope.provider.idle_time = $scope.origProvider.idle_time || DEFAULT_IDLE_TIME;
                    $scope.provider.notifications = $scope.origProvider.notifications;
                    $scope.provider.config = $scope.origProvider.config;
                    $scope.provider.critical_errors = $scope.origProvider.critical_errors;

                    // init the lists of field aliases and non-selected fields
                    $scope.fieldAliases = [];
                    aliases = (angular.isDefined($scope.origProvider.config) && $scope.origProvider.config.field_aliases) || [];

                    var aliasObj = {};
                    aliases.forEach(function (item) {
                        _.extend(aliasObj, item);
                    });

                    Object.keys(aliasObj).forEach(function (fieldName) {
                        $scope.fieldAliases.push(
                            {fieldName: fieldName, alias: aliasObj[fieldName]});
                    });

                    $scope.fieldsNotSelected = $scope.contentFields.filter(
                        function (fieldName) {
                            return !(fieldName in aliasObj);
                        }
                    );
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
                * @param {Object} provider - ingest provider instance
                */
                $scope.setRssConfig = function (provider) {
                    if (!provider.config.auth_required) {
                        provider.config.username = null;
                        provider.config.password = null;
                    }
                    $scope.provider.config = provider.config;
                };

                /**
                * Appends a new (empty) item to the list of field aliases.
                *
                * @method addFieldAlias
                */
                $scope.addFieldAlias = function () {
                    $scope.fieldAliases.push({fieldName: null, alias: ''});
                };

                /**
                * Removes a field alias from the list of field aliases at the
                * specified index.
                *
                * @method removeFieldAlias
                * @param {Number} itemIdx - index of the item to remove
                */
                $scope.removeFieldAlias = function (itemIdx) {
                    var removed = $scope.fieldAliases.splice(itemIdx, 1);
                    if (removed[0].fieldName) {
                        $scope.fieldsNotSelected.push(removed[0].fieldName);
                    }
                };

                /**
                * Updates the list of content field names not selected in any
                * of the dropdown menus.
                *
                * @method fieldSelectionChanged
                */
                $scope.fieldSelectionChanged = function () {
                    var selectedFields = {};

                    $scope.fieldAliases.forEach(function (item) {
                        if (item.fieldName) {
                            selectedFields[item.fieldName] = true;
                        }
                    });

                    $scope.fieldsNotSelected = $scope.contentFields.filter(
                        function (fieldName) {
                            return !(fieldName in selectedFields);
                        }
                    );
                };

                /**
                * Calculates a list of content field names that can be used as
                * options in a dropdown menu.
                *
                * The list is comprised of all field names that are currently
                * not selected in any of the other dropdown menus and
                * of a field name that should be selected in the current
                * dropdown menu (if any).
                *
                * @method availableFieldOptions
                * @param {String} [selectedName] - currently selected field
                * @return {String[]} list of field names
                */
                $scope.availableFieldOptions = function (selectedName) {
                    var fieldNames = angular.copy($scope.fieldsNotSelected);

                    // add current field selection, if available
                    if (selectedName) {
                        fieldNames.push(selectedName);
                    }
                    return fieldNames;
                };

                $scope.save = function() {
                    var newAliases = [];

                    $scope.fieldAliases.forEach(function (item) {
                        if (item.fieldName && item.alias) {
                            var newAlias = {};
                            newAlias[item.fieldName] = item.alias;
                            newAliases.push(newAlias);
                        }
                    });

                    if (typeof($scope.provider.config) !== 'undefined') {
                        $scope.provider.config.field_aliases = newAliases;
                    }
                    delete $scope.provider.all_errors;
                    delete $scope.provider.source_errors;

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
                            if (angular.isDefined(response.data._message)) {
                                notify.error(gettext('Error: ' + response.data._message));
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

                function confirm(context) {
                    if (context === 'scheme') {
                        return modal.confirm(gettext('Are you sure you want to delete this scheme?'));
                    } else if (context === 'rule') {
                        return modal.confirm(gettext('Are you sure you want to delete this scheme rule?'));
                    }
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
                    scope.editScheme.rules = _.reject(scope.editScheme.rules, {name: null});
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
                    confirm('scheme').then(function() {
                        api('routing_schemes').remove(scheme)
                        .then(function(result) {
                            _.remove(scope.schemes, scheme);
                        }, function(response) {
                            if (angular.isDefined(response.data._message)) {
                                notify.error(gettext('Error: ' + response.data._message));
                            } else {
                                notify.error(gettext('There is an error. Routing scheme cannot be deleted.'));
                            }
                        });
                    });
                };

                scope.removeRule = function(rule) {
                    confirm('rule').then(function() {
                        if (rule === scope.rule) {
                            scope.rule = null;
                        }
                        _.remove(scope.editScheme.rules, rule);
                    });
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
                    scope.editScheme.rules.push(rule);
                    scope.editRule(rule);
                };

                scope.editRule = function(rule) {
                    scope.rule = rule;
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

    IngestRoutingGeneral.$inject = ['desks', 'macros'];
    function IngestRoutingGeneral(desks, macros) {
        return {
            scope: {
                rule: '=',
                removeAction: '='
            },
            templateUrl: 'scripts/superdesk-ingest/views/settings/ingest-routing-general.html',
            link: function(scope) {
                scope.typeLookup = typeLookup;
                scope.dayLookup = dayLookup;
                scope.macroLookup = {};

                desks.initialize()
                .then(function() {
                    scope.deskLookup = desks.deskLookup;
                    scope.stageLookup = desks.stageLookup;
                });

                scope.remove = function() {
                    if (typeof scope.removeAction === 'function') {
                        return scope.removeAction(scope.rule);
                    }
                };

                macros.get().then(function(macros) {
                    _.transform(macros, function(lookup, macro, idx) {
                        scope.macroLookup[macro.name] = macro;
                    });
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
                        return g === genre;
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

    IngestRoutingAction.$inject = ['desks', 'macros'];
    function IngestRoutingAction(desks, macros) {
        return {
            scope: {rule: '='},
            templateUrl: 'scripts/superdesk-ingest/views/settings/ingest-routing-action.html',
            link: function(scope) {
                scope.newFetch = {};
                scope.newPublish = {};
                scope.deskLookup = {};
                scope.stageLookup = {};
                scope.macroLookup = {};

                desks.initialize()
                .then(function() {
                    scope.deskLookup = desks.deskLookup;
                    scope.stageLookup = desks.stageLookup;
                });

                macros.get().then(function(macros) {
                    _.transform(macros, function(lookup, macro, idx) {
                        scope.macroLookup[macro.name] = macro;
                    });
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

    IngestDashboardController.$inject = ['$scope', 'api', 'ingestSources', 'preferencesService', 'notify', 'gettext'];
    function IngestDashboardController($scope, $api, ingestSources, preferencesService, notify, gettext) {
        $scope.items = [];
        $scope.dashboard_items = [];

        $scope.fetchItems = function () {
            ingestSources.fetchDashboardProviders().then(function(result) {
                $scope.items = result;
                $scope.dashboard_items =  _.filter(result, {'dashboard_enabled': true});
            });
        };

        $scope.setUserPreferences = function(refresh) {
            var preferences = [];
            var update = {};

            _.forEach(_.filter($scope.items, {'dashboard_enabled': true}),
                function (item) {
                    preferences.push(_.pick(item, _.union(['_id'], _.keys(PROVIDER_DASHBOARD_DEFAULTS))));
                }
            );

            update['dashboard:ingest'] = preferences;
            preferencesService.update(update).then(function(result) {
                if (refresh) {
                    $scope.fetchItems();
                }
            }, function(error) {
                notify.error(gettext('Ingest Dashboard preferences could not be saved.'), 2000);
            });
        };

        $scope.fetchItems();
    }

    IngestUserDashboard.$inject = ['api', 'userList', 'privileges'];
    function IngestUserDashboard (api, userList, privileges) {
        return {
            templateUrl: 'scripts/superdesk-ingest/views/dashboard/ingest-dashboard-widget.html',
            scope: {
                item: '=',
                setUserPreferences: '&'
            },
            link: function (scope) {

                function getCount() {
                    var criteria = {
                            source: {
                                query: {
                                    filtered: {
                                        filter: {
                                            and: [
                                                {term: {ingest_provider: scope.item._id}},
                                                {range: {versioncreated: {gte: 'now-24h'}}}
                                            ]
                                        }
                                    }
                                },
                                size: 0,
                                from: 0
                            }
                        };

                    api.ingest.query(criteria).then(function (result) {
                        scope.ingested_count = result._meta.total;
                    });
                }

                function updateProvider() {
                    api.ingestProviders.getById(scope.item._id).then(function (result) {
                        angular.extend(scope.item, result);
                        getUser();
                    }, function (error) {
                        if (error.status === 404) {
                            scope.item.dashboard_enabled = false;
                            scope.setUserPreferences();
                        }
                    });
                }

                function getLogMessages() {
                    var criteria = {
                        max_results: 5,
                        sort: '[(\'_created\',-1)]',
                        embedded: {user: 1}
                    };

                    var where = [
                            {resource: 'ingest_providers'},
                            {'data.provider_id': scope.item._id}
                        ];

                    if (scope.item.log_messages === 'error') {
                        where.push({name: 'error'});
                    }

                    criteria.where = JSON.stringify ({
                        '$and': where
                    });

                    api.activity.query(criteria).then(function (result) {
                        scope.log_messages = result._items;
                    });
                }

                function refreshItem(data) {
                    if (data.provider_id === scope.item._id) {
                        getCount();
                        updateProvider();
                        getLogMessages();
                    }
                }

                function getUser() {
                    if (scope.item.is_closed && scope.item.last_closed && scope.item.last_closed.closed_by) {
                        userList.getUser(scope.item.last_closed.closed_by).then(function(result) {
                            scope.item.last_closed.display_name = result.display_name;
                        });
                    } else if (!scope.item.is_closed && scope.item.last_opened && scope.item.last_opened.opened_by) {
                        userList.getUser(scope.item.last_opened.opened_by).then(function(result) {
                            scope.item.last_opened.display_name = result.display_name;
                        });
                    }
                }

                function init() {
                    scope.showIngest = Boolean(privileges.privileges.ingest_providers);
                    scope.ingested_count = 0;
                    getCount();
                    getUser();
                    getLogMessages();
                }

                init();

                scope.isIdle = function() {
                    if (scope.item.last_item_update && !scope.item.is_closed) {
                        var idle_time =  scope.item.idle_time || DEFAULT_IDLE_TIME;
                        var last_item_update = moment(scope.item.last_item_update);
                        if (idle_time && !angular.equals(idle_time, DEFAULT_IDLE_TIME)) {
                            last_item_update.add(idle_time.hours, 'h').add(idle_time.minutes, 'm');
                            if (moment() > last_item_update) {
                                return true;
                            }else {
                                return false;
                            }
                        }
                    }
                    return false;
                };

                scope.filterLogMessages = function() {
                    scope.setUserPreferences();
                    getLogMessages();
                };

                scope.$on('ingest:update', function (evt, extras) {
                    refreshItem(extras);
                });

                scope.$on('ingest_provider:update', function (evt, extras) {
                    refreshItem(extras);
                });
            }
        };
    }

    IngestUserDashboardList.$inject = [];
    function IngestUserDashboardList () {
        return {
            templateUrl: 'scripts/superdesk-ingest/views/dashboard/ingest-dashboard-widget-list.html',
            scope: {
                items: '=',
                setUserPreferences: '&'
            }
        };
    }

    IngestUserDashboardDropDown.$inject = ['privileges'];
    function IngestUserDashboardDropDown (privileges) {
        return {
            templateUrl: 'scripts/superdesk-ingest/views/dashboard/ingest-sources-list.html',
            scope: {
                items: '=',
                setUserPreferences: '&'
            },
            link: function (scope) {
                scope.showIngest = Boolean(privileges.privileges.ingest_providers);
            }
        };
    }

    function ScheduleFilter() {
        return function(input) {
            var schedule = '';
            if (_.isPlainObject(input)) {
                schedule += (input.minutes && input.minutes > 0)? (input.minutes + (input.minutes > 1?' minutes':' minute')):'';
                schedule += schedule.length > 0?' ':'';
                schedule += (input.seconds && input.seconds > 0)? (input.seconds + (input.seconds > 1?' seconds':' second')):'';
            }
            return schedule;
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
        .directive('sdUserIngestDashboardDropDown', IngestUserDashboardDropDown)
        .directive('sdUserIngestDashboardList', IngestUserDashboardList)
        .directive('sdUserIngestDashboard', IngestUserDashboard)
        .filter('insert', InsertFilter)
        .filter('scheduleFilter', ScheduleFilter);

    app.config(['superdeskProvider', function(superdesk) {
        superdesk
            .activity('/workspace/ingest', {
                label: gettext('Workspace'),
                priority: 100,
                controller: IngestListController,
                templateUrl: 'scripts/superdesk-archive/views/list.html',
                category: '/workspace',
                topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
                sideTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-sidenav.html',
                privileges: {ingest: 1}
            })
            .activity('/settings/ingest', {
                label: gettext('Ingest'),
                templateUrl: 'scripts/superdesk-ingest/views/settings/settings.html',
                controller: IngestSettingsController,
                category: superdesk.MENU_SETTINGS,
                privileges: {ingest_providers: 1}
            })
            .activity('/ingest_dashboard', {
                label: gettext('Ingest Dashboard'),
                templateUrl: 'scripts/superdesk-ingest/views/dashboard/dashboard.html',
                controller: IngestDashboardController,
                category: superdesk.MENU_MAIN,
                privileges: {ingest_providers: 1}
            })
            .activity('fetchAs', {
                label: gettext('Fetch As'),
                icon: 'archive',
                controller: ['data', 'send', function(data, send) {
                    send.allAs([data.item]);
                }],
                filters: [
                    {action: 'list', type: 'ingest'}
                ],
                privileges: {fetch: 1}
            })
            .activity('archive', {
                label: gettext('Fetch'),
                icon: 'archive',
                monitor: true,
                controller: ['send', 'data', function(send, data) {
                    return send.one(data.item);
                }],
                filters: [
                    {action: 'list', type: 'ingest'}
                ],
                privileges: {fetch: 1},
                key: 'f',
                additionalCondition: ['desks', function (desks) {
                    // fetching to 'personal' desk is not allowed
                    return desks.getCurrentDeskId() != null;
                }]
            })
            .activity('externalsource', {
                label: gettext('Get from external source'),
                icon: 'archive',
                monitor: true,
                controller: ['api', 'data', 'desks', function(api, data, desks) {
                    desks.fetchCurrentDeskId().then(function(deskid) {
                        api(data.item.fetch_endpoint).save({
                            guid: data.item.guid,
                            desk: deskid
                        })
                        .then(
                            function(response) {
                                data.item.error = response;
                            })
                        ['finally'](function() {
                            data.item.actioning.externalsource = false;
                        });
                    });
                }],
                filters: [{action: 'list', type: 'externalsource'}],
                privileges: {fetch: 1}
            })
            .activity('text_archive', {
                label: gettext('Delete from text archive'),
                icon: 'remove',
                monitor: true,
                controller: ['api', 'data', function(api, data) {
                    api
                        .remove(data.item, {}, 'text_archive')
                        .then(
                            function(response) {
                                data.item.error = response;
                            })
                    ['finally'](function() {
                        data.item.actioning.text_archive = false;
                    });
                }],
                filters: [{action: 'list', type: 'text_archive'}],
                privileges: {textarchive: 1}
            });
    }]);

    app.config(['apiProvider', function(apiProvider) {
        apiProvider.api('fetch', {
            type: 'http',
            backend: {
                rel: 'fetch'
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
        apiProvider.api('activity', {
            type: 'http',
            backend: {rel: 'activity'}
        });
    }]);

    SendService.$inject = ['desks', 'api', '$q'];
    function SendService(desks, api, $q) {
        this.one = sendOne;
        this.all = sendAll;

        this.oneAs = sendOneAs;
        this.allAs = sendAllAs;

        this.config = null;
        this.getConfig = getConfig;

        var vm = this;

        /**
         * Send given item to a current user desk
         *
         * @param {Object} item
         * @returns {Promise}
         */
        function sendOne(item) {
            return api
                .save('fetch', {}, {desk: desks.getCurrentDeskId()}, item)
                .then(
                    function(archiveItem) {
                        item.task_id = archiveItem.task_id;
                        item.archived = archiveItem._created;
                    }, function(response) {
                        item.error = response;
                    })
                ['finally'](function() {
                    item.actioning.archive = false;
                });
        }

        /**
         * Send all given items to current user desk
         *
         * @param {Array} items
         */
        function sendAll(items) {
            angular.forEach(items, sendOne);
        }

        /**
         * Send given item using config
         *
         * @param {Object} item
         * @param {Object} config
         * @param {string} config.desk - desk id
         * @param {string} config.stage - stage id
         * @param {string} config.macro - macro name
         * @returns {Promise}
         */
        function sendOneAs(item, config) {
            var data = getData(config);
            return api.save('fetch', {}, data, item).then(function(archived) {
                item.archived = archived._created;
                return archived;
            });

            function getData(config) {
                var data = {
                    desk: config.desk
                };

                if (config.stage) {
                    data.stage = config.stage;
                }

                if (config.macro) {
                    data.macro = config.macro;
                }

                return data;
            }
        }

        /**
         * Send all given item using config once it's resolved
         *
         * At first it only creates a deferred config which is
         * picked by SendItem directive, once used sets the destination
         * it gets resolved and items are sent.
         *
         * @param {Array} items
         * @return {Promise}
         */
        function sendAllAs(items) {
            vm.config = $q.defer();
            return vm.config.promise.then(function(config) {
                vm.config = null;
                return $q.all(items.map(function(item) {
                    return sendOneAs(item, config);
                }));
            });
        }

        /**
         * Get deffered config if any. Used in $watch
         *
         * @returns {Object|null}
         */
        function getConfig() {
            return vm.config;
        }
    }

    return app;

});
