(function() {
'use strict';

/**
 * Mock services that call server on init and thus would require mocking all the time
 */
angular.module('superdesk.mocks', [])
    .provider('config', function() {
        var config = {server: {url: 'http://test'}};
        angular.extend(this, config);
        this.$get = function() {
            return config;
        };
    })
    .service('features', function() {})
    .service('preferencesService', function($q) {
        this.mock = true;

        this.get = function() {
            return $q.when(null);
    	};

        this.update = function() {
            return $q.when(null);
    	};

        this.getPrivileges = function() {
            return $q.when({});
        };
    })
    .service('beta', function($q) {
    	this.isBeta = function() {
    		return $q.when(false);
    	};
    });
})();
