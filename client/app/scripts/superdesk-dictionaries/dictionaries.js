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

    DictionaryService.$inject = ['api', 'urls', '$resource', 'upload'];
    function DictionaryService(api, urls, $resource, upload) {
    	this.dictionaries = null;
    	this.currDictionary = null;

    	this.fetch = function fetch(success, error) {
    		api.dictionaries.query({projection: {content: 0}}).then(success, error);
    	};

        this.open = function open(dictionary, success, error) {
        	var itemURL = urls.item('/dictionaries/:dictId');
        	var dictRes = $resource(itemURL);
        	var dictContent = dictRes.get({dictId: dictionary._id}, function() {
	            dictionary.content = dictContent.content;
	            success(dictionary);
        	}, error);
        };

        this.create = function create(dictionary) {
        	console.log('save', dictionary);
        	urls.resource('dictionary_upload').then(function(uploadURL) {
        		return upload.start({
        			url: uploadURL,
        			method: 'POST',
        			data: dictionary
        		}).then(function(response) {
        			console.log(response);
        		});
        	});
        };

        this.update = function update(dictionary, data, success, error) {
        	return api.save('dictionaries', dictionary, data)
        		.then(success, error);
        };

        this.addWord = function addWord(dictionary, word, success, error) {
            console.log('will add sometime', word, 'to', dictionary);
            return api.save('dictionary_addword', {}, {word:word}, dictionary).then(function(updated) {
                console.log('seems ok', updated);
                return updated;
            }, function(err) {
                console.log('err', err);
            });
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
    		console.log('create');
    		$scope.dictionary = null;
    		$scope.origDictionary = null;
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

    	function init() {
            $scope.dictionary = null;
            $scope.origDictionary = null;
            $scope.dictionaries = null;
	    	$scope.word = {};
    	}

        $scope.save = function() {
        	console.log('dictionary', $scope.dictionary, $scope.origDictionary);
        	if ($scope.dictionary === null) {
        		console.log('create', $scope.dictionary);
        		dictionaries.create($scope.dictionary);
        	} else {
        		dictionaries.update($scope.origDictionary, $scope.dictionary,
        			function(updates) {
        				angular.extend($scope.dictionary, updates);
        				$scope.origDictionary = angular.copy($scope.dictionary);
			            init();
			            $scope.modalActive = false;
	        			return updates;
	        		}, function(response) {
	                    if (angular.isDefined(response.data._issues) &&
	                            angular.isDefined(response.data._issues['validator exception'])) {
	                        notify.error(gettext('Error: ' + response.data._issues['validator exception']));
	                    } else {
	                        notify.error(gettext('Error. Dictionary not updated.'));
	                    }
        		});
        	}
        };

        $scope.cancel = function() {
        	init();
        	$scope.modalActive = false;
        };

        $scope.addWord = function() {
            dictionaries.addWord($scope.dictionary, $scope.word.key);
            $scope.word.key = null;
        };

        init();
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
        });

})();
