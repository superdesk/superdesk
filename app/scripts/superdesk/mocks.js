(function() {
'use strict';

/**
 * Mock services that call server on init and thus would require mocking all the time
 */
angular.module('superdesk.mocks', [])
    .service('features', function() {})
    .service('preferencesService', function($q) {
        this.mock = true;

    	this.get = function() {
    		return $q.when(null);
    	};
    	this.update = function() {
    		return $q.when(null);
    	};
    })
    .service('beta', function($q) {
    	this.isBeta = function() {
    		return $q.when(false);
    	};
    });
})();
