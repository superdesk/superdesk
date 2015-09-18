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

    this.vocabularies = undefined;

    this.getVocabularies = function(scope) {
      if (typeof service.vocabularies === 'undefined') {
        api.query('vocabularies')
            .then(function(result) {
              service.vocabularies = result;
              scope.vocabularies = service.vocabularies;
            });
      } else {
        scope.vocabularies = service.vocabularies;
      }
    };
  };

  VocabularyConfigController.$inject =
      [ '$scope', 'gettext', 'session', 'modal', 'notify', 'vocabularies' ];
  function VocabularyConfigController($scope, gettext, session, modal, notify,
                                      vocabularies) {
    $scope.vocabularies = null;
    $scope.vocabulary = null;

    $scope.createVocabulary = function() {
      $scope.vocabulary = {
        is_active : 'true'
      };
    };

    $scope.openVocabulary = function(vocabulary) {
      $scope.vocabulary = vocabulary;
    };

    $scope.closeVocabulary = function() {
        $scope.vocabulary = null;
    };

    vocabularies.getVocabularies($scope);
  }

  VocabularyEditController.$inject = [
    '$scope',
    'upload',
    'gettext',
    'notify',
    'modal',
    'api',
    'vocabularies'
  ];
  function VocabularyEditController($scope, upload, gettext, notify, modal, api,
                                    vocabularies) {

    function onSuccess(result) {
      $scope.closeVocabulary();
      vocabularies.getVocabularies($scope);
      notify.success(gettext('Vocabulary saved succesfully'));
      $scope.progress = null;
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
        width : 1
      };
      api.save('vocabularies', $scope.vocabulary).then(onSuccess, onError);
    };

    $scope.cancel = function() {
      $scope._errorUniqueness = false;
      $scope.closeVocabulary();
      $scope.model = null;
    };

    var model = {};
    _.each(
      _.sortBy($scope.vocabulary.items, function(item) {return -_.size(item)})[0],
      function(v, k) { model[k] = null; }
    );
    $scope.model = model;
    console.log(
        _.sortBy($scope.vocabulary.items, function(o) { return -_.size(o) })
    );
  }

  var app = angular.module('superdesk.vocabularies',
                           [ 'superdesk.activity']);

  app.config([
    'superdeskProvider',
    function(superdesk) {
      superdesk.activity('/settings/vocabularies', {
        label : gettext('Vocabularies'),
        controller : VocabularyConfigController,
        templateUrl : 'scripts/superdesk-vocabularies/views/settings.html',
        category : superdesk.MENU_SETTINGS,
        priority : -800,
        privileges : {vocabularies : 1}
      });
    }
  ])
      .service('vocabularies', VocabularyService)
      .controller('VocabularyEdit', VocabularyEditController)
      .controller('VocabularyConfig', VocabularyConfigController)
      .directive('sdVocabularyConfig',
                 function() {
                   return {
                     controller : VocabularyConfigController
                   };
                 })
      .directive('sdVocabularyConfigModal', function() {
        return {
          controller : 'VocabularyEdit',
          require : '^sdVocabularyConfig',
          templateUrl :
              'scripts/superdesk-vocabularies/views/vocabulary-config-modal.html'
        };
      });
})();
