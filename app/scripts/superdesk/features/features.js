(function() {
'use strict';

Features.$inject = ['urls'];
function Features(urls) {
    var self = this;
    urls.links().then(function(links) {
        angular.extend(self, links);
    });
}

/**
 * Provides info what features are available on server
 */
angular.module('superdesk.features', ['superdesk.api'])
    .service('features', Features);

})();
