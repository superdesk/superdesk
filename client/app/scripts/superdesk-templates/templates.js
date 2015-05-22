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

    TemplatesService.$inject = ['api', '$q', 'gettext'];
    function TemplatesService(api, $q, gettext) {

        this.types = [
            {_id: 'kill', label: gettext('Kill')},
            {_id: 'create', label: gettext('Create')}
        ];

        this.fetchContentTemplates = function fetchContentTemplates() {
            return api.find('content_templates');
        };
    }

    TemplatesDirective.$inject = ['gettext', 'notify', 'api', 'templates', 'modal', 'adminPublishSettingsService'];
    function TemplatesDirective(gettext, notify, api, templates, modal, adminPublishSettingsService) {
        return {
            templateUrl: 'scripts/superdesk-templates/views/templates.html',
            link: function ($scope) {
                $scope.content_templates = null;
                $scope.origTemplate = null;
                $scope.template = null;

                function fetchTemplates() {
                    templates.fetchContentTemplates().then(
                        function(content_templates) {
                            $scope.content_templates = content_templates;
                        }
                    );
                }

                $scope.types = templates.types;

                $scope.save = function() {
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

                    $scope.item = $scope.template;
                    $scope._editable = true;

                    $scope.origTemplate.destination_groups = $scope.origTemplate.destination_groups || [];

                    if ($scope.origTemplate.destination_groups && $scope.origTemplate.destination_groups.length) {
                        adminPublishSettingsService.fetchDestinationGroupsByIds($scope.origTemplate.destination_groups)
                            .then(function(result) {
                                var destinationGroups = [];
                                _.each(result._items, function(item) {
                                    destinationGroups.push(item);
                                });
                                $scope.vars = {destinationGroups: destinationGroups};
                            });
                    } else {
                        $scope.vars = {destinationGroups: []};
                    }
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

                $scope.$watch('vars', function() {
                    if ($scope.vars && $scope.vars.destinationGroups) {
                        var destinationGroups = _.pluck($scope.vars.destinationGroups, '_id').sort();
                        if (!_.isEqual(destinationGroups, $scope.template.destination_groups)) {
                            $scope.template.destination_groups = destinationGroups;
                        }
                    }
                }, true);

                fetchTemplates();
            }
        };
    }

    CreateTemplateController.$inject = ['item', 'templates', 'api', 'desks', '$q'];
    function CreateTemplateController(item, templates, api, desks, $q) {
        var vm = this,
            metadata = [
                'headline',
                'slugline',
                'abstract',
                'dateline',
                'byline',
                'usage_terms',
                'subject',
                'genre',
                'type',
                'language',
                'anpa-category',
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
                'creditline'
            ];

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
            }, _.pick(item, metadata));
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

    angular.module('superdesk.templates', ['superdesk.activity', 'superdesk.authoring'])
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
