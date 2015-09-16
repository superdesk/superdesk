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

    var app = angular.module('superdesk.vocabularies', ['superdesk.users']);

    /**
     * Controller for Vocabularies Settings page. Each vocabulary will be displayed if user has a privilege.
     */
    VocabulariesSettingsController.$inject = ['$scope', 'privileges'];
    function VocabulariesSettingsController($scope, privileges) {
        var user_privileges = privileges.privileges;

        $scope.showKeywordsVocabulary  = Boolean(user_privileges.vocabulary_keywords);
    }

    /**
     * Directive to manage Keywords vocabulary
     */
    KeywordsVocabularyDirective.$inject = ['metadata', 'gettext', 'notify', 'api', 'modal'];
    function KeywordsVocabularyDirective(metadata, gettext, notify, api, modal) {
        return {
            templateUrl: 'scripts/superdesk-vocabularies/views/keywords.html',
            link: function ($scope) {
                $scope.editKeyword = null;

                /**
                 * Fetches active keywords from the vocabulary and assigns the collection to $scope.keywords.
                 * If fetched successfully then updates the keywords collection in metadata.values.
                 */
                function fetchActiveKeywords() {
                    api.vocabulary_keywords.query({
                        where: JSON.stringify({'is_active': true})
                    }).then(function(result) {
                        $scope.keywords = result._items;

                        if (!_.isEmpty($scope.keywords)) {
                            if (angular.isDefined(metadata.values)) {
                                updateKeywordsInMetadata();
                            } else {
                                metadata.fetchMetadataValues().then(updateKeywordsInMetadata);
                            }
                        }
                    });
                }

                /**
                 * Updates the keywords vocabulary in the vocabulary collection represented by metadata.values.
                 */
                function updateKeywordsInMetadata() {
                    var keywordsVocabulary = [];

                    _.each($scope.keywords, function(keyword, index, keywords) {
                        keywordsVocabulary.push(_.pick(keyword, ['name', 'value']));
                    });

                    metadata.values.keywords = keywordsVocabulary;
                }

                /**
                 * Upserts a keyword. If the operation is successful then fetches the active keywords and
                 * re-draws the view.
                 */
                $scope.save = function() {
                    api.vocabulary_keywords.save($scope.originalKeyword, $scope.editKeyword)
                        .then(
                            function() {
                                notify.success(gettext('Keyword saved.'));
                                $scope.cancel();
                            },
                            function(response) {
                                if (angular.isDefined(response.data) && angular.isDefined(response.data._issues)) {
                                    if (angular.isDefined(response.data._issues['validator exception'])) {
                                        notify.error(gettext('Error: ' + response.data._issues['validator exception']));
                                    }
                                } else {
                                    notify.error(gettext('Error: Failed to save Keyword.'));
                                }
                            }
                        )
                        .then(fetchActiveKeywords);
                };

                /**
                 * Initializes the editForm for the keyword.
                 */
                $scope.edit = function(keyword) {
                    $scope.editKeyword = _.create(keyword);
                    $scope.originalKeyword = keyword;
                };

                /**
                 * Removes the keyword from the vocabulary. If the operation is successful then fetches the
                 * active keywords and re-draws the view.
                 */
                $scope.remove = function (keyword) {
                    modal.confirm(gettext('Are you sure you want to delete keyword?'))
                        .then(function() {
                            api.vocabulary_keywords.remove(keyword).then(
                                function(result) {
                                    fetchActiveKeywords();
                                },
                                function(response) {
                                    if (angular.isDefined(response.data) && angular.isDefined(response.data._message)) {
                                        notify.error(gettext('Error: ' + response.data._message));
                                    } else {
                                        notify.error(gettext('There is an error. Keyword cannot be deleted.'));
                                    }
                                });
                        });
                };

                /**
                 * Closes the editForm modal
                 */
                $scope.cancel = function() {
                    $scope.editKeyword = null;
                };

                fetchActiveKeywords();
            }
        };
    }

    app
        .directive('sdAdminVocKeywords', KeywordsVocabularyDirective);

    app
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/settings/vocabularies', {
                    label: gettext('Vocabularies'),
                    templateUrl: 'scripts/superdesk-vocabularies/views/settings.html',
                    controller: VocabulariesSettingsController,
                    category: superdesk.MENU_SETTINGS,
                    privileges: {vocabulary_keywords: 1},
                    priority: 3000,
                    beta: false
                });
        }])
        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('vocabulary_keywords', {
                type: 'http',
                backend: {
                    rel: 'vocabulary_keywords'
                }
            });
        }]);

    return app;
})();
