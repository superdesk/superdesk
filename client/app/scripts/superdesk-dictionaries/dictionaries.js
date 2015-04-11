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

    DictionaryService.$inject = ['api', 'urls', '$resource', '$upload'];
    function DictionaryService(api, urls, $resource, $upload) {
        this.dictionaries = null;
        this.currDictionary = null;

        this.fetch = function fetch(success, error) {
            api.dictionaries.query({projection: {content: 0}}).then(success, error);
        };

        this.open = function open(dictionary, success, error) {
            api.find('dictionaries', dictionary._id, {projection: {content: 0}}).then(success, error);
        };

        this.upload = function create(dictionary, file, success, error) {
            var hasId = _.has(dictionary, '_id') && dictionary._id !== null;
            var method = hasId ? 'PATCH' : 'POST';
            var headers = hasId ? {'If-Match': dictionary._etag} : {};
            var data = {
                'name': dictionary.name,
                'language_id': dictionary.language_id
            };

            urls.resource('dictionaries').then(function(uploadURL) {
                if (hasId) {
                    uploadURL += '/' + dictionary._id;
                }
                return $upload.upload({
                    url: uploadURL,
                    method: method,
                    data: data,
                    file: file,
                    headers: headers
                }).then(success, error);
            }, error);
        };

        this.update = function update(dictionary, data, success, error) {
            return api.save('dictionaries', dictionary, data).then(success, error);
        };

        this.addWord = function addWord(dictionary, word, success, error) {
            return api.save('dictionary_addword', {}, {word:word}, dictionary)
                .then(function(updates) {
                    api.find('dictionaries', dictionary._id).then(function(doc) {
                        return success(doc, updates);
                    }, error);
                }, error);
        };

        this.remove = function remove(dictionary, success, error) {
            return api.remove(dictionary).then(success, error);
        };
    }

    DictionaryConfigController.$inject = ['$scope', 'dictionaries', 'gettext', 'modal', 'notify'];
    function DictionaryConfigController ($scope, dictionaries, gettext, modal, notify) {
        $scope.dictionaries = null;
        $scope.origDictionary = null;
        $scope.dictionary = null;

        var fetchDictionaries = function() {
            dictionaries.fetch(function(result) {
                $scope.dictionaries = result;
            });
        };

        $scope.createDictionary = function() {
            $scope.dictionary = {};
            $scope.origDictionary = {};
            $scope.modalActive = true;
        };

        $scope.openDictionary = function(dictionary) {
            dictionaries.open(dictionary, function(result) {
                $scope.dictionary = result;
                $scope.origDictionary = angular.copy($scope.dictionary);
                $scope.modalActive = true;
            });
        };

        $scope.remove = function(dictionary) {
            modal.confirm(gettext('Please confirm you want to delete dictionary.')).then(
                function runConfirmed() {
                    dictionaries.remove(dictionary, function() {
                        _.remove($scope.dictionaries._items, dictionary);
                        notify.success(gettext('Dictionary deleted.'), 3000);
                    });
                }
            );
        };

        fetchDictionaries();
    }

    DictionaryConfigModalController.$inject = ['$scope', 'dictionaries', 'upload', 'gettext', 'notify', 'modal'];
    function DictionaryConfigModalController ($scope, dictionaries, upload, gettext, notify, modal) {
        function reset() {
            $scope.dictionary = null;
            $scope.origDictionary = null;
            $scope.word = {};
            $scope.file = null;
            $scope.modalActive = false;
        }

        var onSuccess = function(result) {
            reset();
            dictionaries.fetch(function(result) {
                $scope.dictionaries = result;
            });
            notify.success(gettext('Dictionary saved succesfully'));
            return result;
        };

        var onError = function(response) {
            if (angular.isDefined(response.data._issues) &&
                    angular.isDefined(response.data._issues['validator exception'])) {
                notify.error(gettext('Error: ' + response.data._issues['validator exception']));
            } else {
                notify.error(gettext('Error. Dictionary not saved.'));
            }
        };

        //listen for the file selected event
        $scope.$on('fileSelected', function (event, args) {
            $scope.$apply(function() {
                $scope.file = args.file;
            });
        });

        $scope.canSave = function(form) {
            var hasId = _.has($scope.dictionary, '_id') && $scope.dictionary._id !== null;
            return form.$valid && (form.$dirty || $scope.file !== null) && (!hasId && $scope.file !== null || hasId);
        };

        $scope.save = function() {
            if ($scope.file) {
                dictionaries.upload($scope.dictionary, $scope.file, onSuccess, onError);
            } else {
                dictionaries.update($scope.origDictionary, $scope.dictionary, onSuccess, onError);
            }
        };

        $scope.cancel = function() {
            reset();
        };

        $scope.addWord = function() {
            dictionaries.addWord($scope.dictionary, $scope.word.key,
                function(updated, updates) {
                    _.assign($scope.dictionary, _.omit(updated, ['content', 'word']));
                    $scope.word.key = null;
                    notify.success(gettext('Word added succesfully: ') + updates.word);
                }, onError);
        };

        reset();
    }

    var app = angular.module('superdesk.dictionaries', []);

    app
        .config(['superdeskProvider', function(superdesk) {
            superdesk
            .activity('/settings/dictionaries', {
                    label: gettext('Dictionaries'),
                    controller: DictionaryConfigController,
                    templateUrl: 'scripts/superdesk-dictionaries/views/settings.html',
                    category: superdesk.MENU_SETTINGS,
                    priority: -800,
                    privileges: {dictionaries: 1}
                });
        }])
        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('dictionaries', {
                type: 'http',
                backend: {
                    rel: 'dictionaries'
                }
            });
        }])
        .service('dictionaries', DictionaryService)
        .directive('sdDictionaryConfig', function() {
            return {
                controller: DictionaryConfigController
            };
        })
        .directive('sdDictionaryConfigModal', function() {
            return {
                scope: {
                    modalActive: '=active',
                    dictionaries: '=',
                    dictionary: '=',
                    origDictionary: '=',
                    word: '=',
                    cancel: '&'
                },
                controller: DictionaryConfigModalController,
                require: '^sdDictionaryConfig',
                templateUrl: 'scripts/superdesk-dictionaries/views/dictionary-config-modal.html',
                link: function(scope, elem, attrs, ctrl) {
                }
            };
        }).directive('fileUpload', function () {
            return {
                scope: true,
                link: function (scope, element, attrs) {
                    element.bind('change', function (event) {
                        scope.$emit('fileSelected', {file: event.target.files[0]});
                    });
                }
            };
        });
})();
