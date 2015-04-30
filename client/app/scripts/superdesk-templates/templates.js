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

    TemplatesSettingsService.$inject = ['api', '$q'];
    function TemplatesSettingsService(api, $q) {

        this.fetchTemplates = function fetchTemplates() {
            return api.find('templates');
        };

        this.fetchContentTemplates = function fetchContentTemplates() {
            return api.find('content_templates');
        };
    }

    TemplatesDirective.$inject = ['gettext', 'notify', 'api', 'templatesSettingsService', 'modal', 'adminPublishSettingsService'];
    function TemplatesDirective(gettext, notify, api, templatesSettingsService, modal, adminPublishSettingsService) {
        return {
            templateUrl: 'scripts/superdesk-templates/views/templates.html',
            link: function ($scope) {
                $scope.templates = null;
                $scope.content_templates = null;
                $scope.origTemplate = null;
                $scope.template = null;

                function fetchTemplates() {
                    templatesSettingsService.fetchTemplates().then(
                        function(result) {
                            $scope.templates = result;
                            templatesSettingsService.fetchContentTemplates().then(
                                function(content_templates) {
                                    $scope.content_templates = content_templates;
                                }
                            );
                        }
                    );
                }

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

    var app = angular.module('superdesk.templates', ['superdesk.authoring']);
    app.service('templatesSettingsService', TemplatesSettingsService)
        .directive('sdTemplates', TemplatesDirective);

    app
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/settings/templates', {
                    label: gettext('Templates'),
                    templateUrl: 'scripts/superdesk-templates/views/settings.html',
                    controller: TemplatesSettingsController,
                    category: superdesk.MENU_SETTINGS,
                    privileges: {content_templates: 1},
                    priority: 2000,
                    beta: true
                });
        }])
        .config(['apiProvider', function(apiProvider) {
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
        }]);

    return app;
})();
