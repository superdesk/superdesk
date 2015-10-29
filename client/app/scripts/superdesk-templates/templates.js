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

        this.types = [
            {_id: 'kill', label: gettext('Kill')},
            {_id: 'create', label: gettext('Create')},
            {_id: 'highlights', label: gettext('Highlights')}
        ];

        this.fetchTemplates = function fetchTemplates(page, pageSize, type, desk, keyword) {
            page = page || 1;
            pageSize = pageSize || PAGE_SIZE;

            var criteria = {};
            if (type !== undefined) {
                criteria.template_type = type;
            }
            if (desk !== undefined) {
                criteria.template_desk = desk;
            }
            if (keyword) {
                criteria.template_name = {'$regex': keyword, '$options': '-i'};
            }
            var params = {
                max_results: pageSize,
                page: page
            };
            if (!_.isEmpty(criteria)) {
                params.where = JSON.stringify({
                    '$and': [criteria]
                });
            }
            return api.content_templates.query(params)
            .then(function(result) {
                return result;
            });
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

            return api.content_templates.query(params)
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
                    api.content_templates.save($scope.origTemplate, $scope.template)
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
                    $scope.origTemplate = template || {'type': 'text'};
                    $scope.template = _.create($scope.origTemplate);
                    $scope.template.schedule = $scope.origTemplate.schedule || {};

                    $scope.item = $scope.template;
                    $scope._editable = true;
                    $scope.updateStages($scope.template.template_desk);
                };

                $scope.remove = function(template) {
                    modal.confirm(gettext('Are you sure you want to delete the template?'))
                        .then(function() {
                            return api.content_templates.remove(template);
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
                };

                $scope.updateStages = function(desk) {
                    $scope.stages = desk ? desks.deskStages[desk] : null;
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

        this.types = templates.types;
        this.save = save;

        activate();

        function activate() {
            desks.fetchCurrentUserDesks().then(function(desks) {
                vm.desks = desks._items;
            });
        }

        function save() {
            var template = angular.extend({
                template_name: vm.name,
                template_type: vm.type,
                template_desk: vm.desk
            }, _.pick(item, templates.TEMPLATE_METADATA));
            return api.save('content_templates', template).then(function(data) {
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

    angular.module('superdesk.templates', ['superdesk.activity', 'superdesk.authoring', 'superdesk.preferences'])
        .service('templates', TemplatesService)
        .directive('sdTemplates', TemplatesDirective)
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
            priority: 2000,
            beta: true
        });

        apiProvider.api('templates', {
            type: 'http',
            backend: {
                rel: 'templates'
            }
        });

        apiProvider.api('content_templates', {
            type: 'http',
            backend: {
                rel: 'content_templates'
            }
        });
    }
})();
