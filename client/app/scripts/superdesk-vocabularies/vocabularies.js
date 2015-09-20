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

    VocabularyService
        .$inject = [ 'api', 'urls', 'session', '$q'];
    function VocabularyService(api, urls, session, $q) {
        var service = this;

        this.getVocabularies = function() {
            if (typeof service.vocabularies === 'undefined') {
                return api.query('vocabularies')
                .then(function(result) {
                    service.vocabularies = result;
                    return $q.when(service.vocabularies);
                });
            } else {
                return $q.when(service.vocabularies);
            }
        };
    }

    VocabularyConfigController.$inject = ['$scope', 'vocabularies'];
    function VocabularyConfigController($scope, vocabularies) {

        $scope.openVocabulary = function(vocabulary) {
            $scope.vocabulary = vocabulary;
        };

        vocabularies.getVocabularies().then(function(vocabularies) {
            $scope.vocabularies = vocabularies;
        });
    }

    VocabularyEditController.$inject = [
      '$scope',
      'gettext',
      'notify',
      'api',
      'vocabularies',
    ];
    function VocabularyEditController($scope, gettext, notify, api, vocabularies) {

        function closeVocabulary() {
            $scope.vocabulary = null;
        }

        function onSuccess(result) {
            notify.success(gettext('Vocabulary saved succesfully'));
            closeVocabulary();
            return result;
        }

        function onError(response) {
            if (angular.isDefined(response.data._issues)) {
                if (angular.isDefined(response.data._issues['validator exception'])) {
                    notify.error(gettext('Error: ' +
                                         response.data._issues['validator exception']));
                } else {
                    notify.error(gettext('Error. Vocabulary not saved.'));
                }
            }
            $scope.progress = null;
        }

        $scope.addItem = function() {
            $scope.vocabulary.items.push(model);
        };

        $scope.removeItem = function(item) {
            $scope.vocabulary.items.splice($scope.vocabulary.items.indexOf(item), 1);
        };

        $scope.save = function() {
            $scope._errorUniqueness = false;
            $scope.progress = {
                width: 1
            };
            api.save('vocabularies', $scope.vocabulary).then(onSuccess, onError);
        };

        $scope.cancel = function() {
            closeVocabulary();
        };

        var model = _.mapValues(_.indexBy(
            _.uniq(_.flatten(
                _.map($scope.vocabulary.items, function(o) { return _.keys(o); })
            ))
        ), function() { return null; });
        $scope.model = model;
    }

    var app = angular.module('superdesk.vocabularies',
                             [ 'superdesk.activity']);
    app.config([
      'superdeskProvider',
      function(superdesk) {
          superdesk.activity('/settings/vocabularies', {
              label: gettext('Vocabularies'),
              templateUrl: 'scripts/superdesk-vocabularies/views/settings.html',
              category: superdesk.MENU_SETTINGS,
              priority: -800,
              privileges: {vocabularies: 1}
          });
      }
    ])
    .service('vocabularies', VocabularyService)
    .controller('VocabularyEdit', VocabularyEditController)
    .controller('VocabularyConfig', VocabularyConfigController)
    .directive('sdVocabularyConfig', function() {
        return {
            scope: {
                vocabulary: '=',
            },
            controller: 'VocabularyConfig',
            templateUrl: 'scripts/superdesk-vocabularies/views/vocabulary-config.html'
        };
    })
    .directive('sdVocabularyConfigModal', function() {
        return {
            scope: {
                vocabulary: '=',
            },
            controller: 'VocabularyEdit',
            templateUrl: 'scripts/superdesk-vocabularies/views/vocabulary-config-modal.html'
        };
    });
})();
