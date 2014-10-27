(function() {
'use strict';

/**
 * Mock services that call server on init and thus would require mocking all the time
 */
angular.module('superdesk.mocks', [])
    .service('features', function() {});

})();
