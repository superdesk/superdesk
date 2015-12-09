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

    var KILL_TEMPLATE_IGNORE_FIELDS = ['dateline', 'template_desk', 'template_stage',
        'schedule', 'next_run', 'last_run'];

    TemplatesSettingsController.$inject = ['$scope'];
    function TemplatesSettingsController($scope) {

    }

    TemplatesService.$inject = ['api', '$q', 'gettext', 'preferencesService'];
    function TemplatesService(api, $q, gettext, preferencesService) {
        var PAGE_SIZE = 10;
        var PREFERENCES_KEY = 'templates:recent';

        this.TEMPLATE_METADATA = [
            'headline',
            'slugline',
            'abstract',
            'dateline',
            'byline',
            'subject',
            'genre',
            'type',
            'language',
            'anpa_category',
            'anpa_take_key',
            'keywords',
            'priority',
            'urgency',
            'pubstatus',
            'description',
            'body_html',
            'body_text',
            'place',
            'located',
            'creditline',
            'ednote',
            'language'
        ];

        /**
         * Filter out item data that is not usable for template
         *
         * @param {Object} item
         * @return {Object}
         */
        this.pickItemData = function(item) {
            return _.pick(item, this.TEMPLATE_METADATA);
        };

        this.types = [
            {_id: 'kill', label: gettext('Kill')},
            {_id: 'create', label: gettext('Create')},
            {_id: 'highlights', label: gettext('Highlights')}
        ];

        this.fetchTemplates = function fetchTemplates(page, pageSize, type, desk, user, keyword) {
            var params = {
                page: page || 1,
                max_results: pageSize || PAGE_SIZE
            };

            var criteria = {};

            if (type !== undefined) {
                criteria.template_type = type;
            }

            if (keyword) {
                criteria.template_name = {'$regex': keyword, '$options': '-i'};
            }

            if (user || desk) {
                criteria.$or = [];

                if (user) { // user private templates
                    criteria.$or.push({user: user, is_public: false});
                }

                if (desk) { // all non private desk templates
                    criteria.$or.push({template_desk: desk, is_public: {$ne: false}});
                }
            } else {
                // only show public templates
                criteria.is_public = {$ne: false};
            }

            if (!_.isEmpty(criteria)) {
                params.where = JSON.stringify({
                    '$and': [criteria]
                });
            }

            return api.query('content_templates', params);
        };

        this.fetchTemplatesByIds = function(templateIds) {
            if (!templateIds.length) {
                return $q.when();
            }

            var params = {
                max_results: PAGE_SIZE,
                page: 1,
                where: JSON.stringify({_id: {'$in': templateIds}})
            };

            return api.query('content_templates', params)
            .then(function(result) {
                if (result && result._items) {
                    result._items.sort(function(a, b) {
                        return templateIds.indexOf(a._id) - templateIds.indexOf(b._id);
                    });
                }
                return result;
            });
        };

        this.addRecentTemplate = function(deskId, templateId) {
            return preferencesService.get()
            .then(function(result) {
                result = result || {};
                result[PREFERENCES_KEY] = result[PREFERENCES_KEY] || {};
                result[PREFERENCES_KEY][deskId] = result[PREFERENCES_KEY][deskId] || [];
                _.remove(result[PREFERENCES_KEY][deskId], function(i) {
                    return i === templateId;
                });
                result[PREFERENCES_KEY][deskId].unshift(templateId);
                return preferencesService.update(result);
            });
        };

        this.getRecentTemplateIds = function(deskId, limit) {
            limit = limit || PAGE_SIZE;
            return preferencesService.get()
            .then(function(result) {
                if (result && result[PREFERENCES_KEY] && result[PREFERENCES_KEY][deskId]) {
                    return _.take(result[PREFERENCES_KEY][deskId], limit);
                }
                return [];
            });
        };

        this.getRecentTemplates = function(deskId, limit) {
            limit = limit || PAGE_SIZE;
            return this.getRecentTemplateIds(deskId, limit)
                .then(this.fetchTemplatesByIds);
        };
    }

    TemplatesDirective.$inject = ['gettext', 'notify', 'api', 'templates', 'modal', 'desks', 'weekdays', '$filter'];
    function TemplatesDirective(gettext, notify, api, templates, modal, desks, weekdays, $filter) {
        return {
            templateUrl: 'scripts/superdesk-templates/views/templates.html',
            link: function ($scope) {
                $scope.weekdays = weekdays;
                $scope.content_templates = null;
                $scope.origTemplate = null;
                $scope.template = null;
                $scope.desks = null;

                function fetchTemplates() {
                    templates.fetchTemplates(1, 50).then(
                        function(result) {
                            result._items = $filter('sortByName')(result._items, 'template_name');
                            $scope.content_templates = result;
                        }
                    );
                }

                desks.initialize().then(function() {
                    $scope.desks = desks.desks;
                });

                /*
                 * Returns desk name
                 */
                $scope.getTemplateDesk = function getTemplateDesk(template) {
                    return _.find($scope.desks._items , {_id: template.template_desk});
                };

                /*
                 * Returns stage name
                 */
                $scope.getTemplateStage = function getTemplateStage(template) {
                    return _.find(desks.stages._items , {_id: template.template_stage});
                };

                /*
                 * Convert string to time object
                 *
                 * @param {String}{%M%S} time
                 * @return {Object} d Returns time object
                 */
                $scope.getTime = function getTime(time) {
                    if (time) {
                        var d = new Date();

                        d.setUTCHours(time.substr(0, 2));
                        d.setUTCMinutes(time.substr(2, 2));

                        return d;
                    }
                };

                $scope.types = templates.types;

                $scope.save = function() {
                    delete $scope.template._datelinedate;
                    delete $scope.template.hasCrops;
                    var template = $scope.template;
                    // certain field are not required for kill template
                    if (template && template.template_type === 'kill') {
                        template = _.omit($scope.template, KILL_TEMPLATE_IGNORE_FIELDS);
                    }

                    api.save('content_templates', $scope.origTemplate, template)
                        .then(
                            function() {
                                notify.success(gettext('Template saved.'));
                                $scope.cancel();
                            },
                            function(response) {
                                if (angular.isDefined(response.data._issues) &&
                                    angular.isDefined(response.data._issues['validator exception'])) {
                                    notify.error(gettext('Error: ' + response.data._issues['validator exception']));
                                } else {
                                    notify.error(gettext('Error: Failed to save template.'));
                                }
                            }
                        ).then(fetchTemplates);
                };

                $scope.edit = function(template) {
                    $scope.origTemplate = template || {type: 'text', is_public: true};
                    $scope.template = _.create($scope.origTemplate);
                    $scope.template.schedule = $scope.origTemplate.schedule || {};
                    $scope.template.data = $scope.origTemplate.data || {};
                    $scope.template.is_public = $scope.template.is_public !== false;
                    $scope.item = $scope.template.data;
                    $scope._editable = true;
                    $scope.updateStages($scope.template.template_desk);
                };

                $scope.remove = function(template) {
                    modal.confirm(gettext('Are you sure you want to delete the template?'))
                        .then(function() {
                            return api.remove(template);
                        })
                        .then(function(result) {
                            _.remove($scope.templates, template);
                        }, function(response) {
                            if (angular.isDefined(response.data._message)) {
                                notify.error(gettext('Error: ' + response.data._message));
                            } else {
                                notify.error(gettext('There is an error. Template cannot be deleted.'));
                            }
                        })
                        .then(fetchTemplates);
                };

                $scope.cancel = function() {
                    $scope.origTemplate = null;
                    $scope.template = null;
                    $scope.vars = null;
                    fetchTemplates();
                };

                $scope.updateStages = function(desk) {
                    $scope.stages = desk ? desks.deskStages[desk] : null;
                };

                $scope.validSchedule = function() {
                    return $scope.template.schedule.is_active ?
                        $scope.template.schedule.day_of_week && $scope.template.schedule.create_at :
                        true;
                };

                fetchTemplates();
            }
        };
    }

    CreateTemplateController.$inject = ['item', 'templates', 'api', 'desks', '$q'];
    function CreateTemplateController(item, templates, api, desks, $q) {
        var vm = this;

        this.type = 'create';
        this.name = item.slugline || null;
        this.desk = desks.active.desk || null;
        this.is_public = false;

        this.types = templates.types;
        this.save = save;

        activate();

        function activate() {
            if (item.template) {
                api.find('content_templates', item.template).then(function(template) {
                    vm.name = template.template_name;
                    vm.desk = template.template_desk || null;
                    vm.is_public = template.is_public !== false;
                    vm.template = template;
                });
            }

            desks.fetchCurrentUserDesks().then(function(desks) {
                vm.desks = desks._items;
            });
        }

        function save() {
            var data = {
                template_name: vm.name,
                template_type: vm.type,
                template_desk: vm.is_public ? vm.desk : null,
                is_public: vm.is_public,
                data: templates.pickItemData(item)
            };

            var template = vm.template ? vm.template : data;
            var diff = vm.template ? data : null;

            // in case there is old template but user renames it - create a new one
            if (vm.template && vm.name !== vm.template.template_name) {
                template = data;
                diff = null;
            }

            return api.save('content_templates', template, diff)
            .then(function(data) {
                vm._issues = null;
                return data;
            }, function(response) {
                vm._issues = response.data._issues;
                return $q.reject(vm._issues);
            });
        }
    }

    TemplateMenuController.$inject = ['$modal'];
    function TemplateMenuController($modal) {
        this.create = createFromItem;
        function createFromItem(item) {
            $modal.open({
                templateUrl: 'scripts/superdesk-templates/views/create-template.html',
                controller: 'CreateTemplateController',
                controllerAs: 'template',
                resolve: {
                    item: function() {
                        return item;
                    }
                }
            });
        }
    }

    TemplateSelectDirective.$inject = ['api', 'desks', 'session', 'templates'];
    function TemplateSelectDirective(api, desks, session, templates) {
        var PAGE_SIZE = 200;

        return {
            templateUrl: 'scripts/superdesk-templates/views/sd-template-select.html',
            scope: {
                selectAction: '=',
                open: '='
            },
            link: function(scope) {
                scope.options = {
                    keyword: null,
                };

                scope.close = function() {
                    scope.open = false;
                };

                scope.select = function(template) {
                    scope.selectAction(template);
                    scope.close();
                };

                /**
                 * Fetch templates and assign it to scope but split it into public/private
                 */
                function fetchTemplates() {
                    templates.fetchTemplates(scope.options.page, PAGE_SIZE, 'create',
                        desks.activeDeskId, session.identity._id, scope.options.keyword)
                    .then(function(result) {
                        scope.publicTemplates = [];
                        scope.privateTemplates = [];
                        result._items.forEach(function(template) {
                            if (template.is_public !== false) {
                                scope.publicTemplates.push(template);
                            } else {
                                scope.privateTemplates.push(template);
                            }
                        });
                    });
                }

                scope.$watch('options.keyword', fetchTemplates);
            }
        };
    }

    function TemplateListDirective() {
        var ENTER = 13;
        return {
            scope: {templates: '=', select: '&'},
            templateUrl: 'scripts/superdesk-templates/views/template-list.html',
            link: function(scope) {
                /**
                 * Call select on keyboard event if key was enter
                 *
                 * @param {Event} $event
                 * @param {Object} template
                 */
                scope.selectOnEnter = function($event, template) {
                    if ($event.key === ENTER) {
                        scope.select(template);
                    }
                };
            }
        };
    }

    angular.module('superdesk.templates', ['superdesk.activity', 'superdesk.authoring', 'superdesk.preferences'])
        .service('templates', TemplatesService)
        .directive('sdTemplates', TemplatesDirective)
        .directive('sdTemplateSelect', TemplateSelectDirective)
        .directive('sdTemplateList', TemplateListDirective)
        .controller('CreateTemplateController', CreateTemplateController)
        .controller('TemplateMenu', TemplateMenuController)
        .config(config)
        ;

    config.$inject = ['superdeskProvider', 'apiProvider'];
    function config(superdesk, apiProvider) {
        superdesk.activity('/settings/templates', {
            label: gettext('Templates'),
            templateUrl: 'scripts/superdesk-templates/views/settings.html',
            controller: TemplatesSettingsController,
            category: superdesk.MENU_SETTINGS,
            privileges: {content_templates: 1},
            priority: 2000
        });
    }
})();
