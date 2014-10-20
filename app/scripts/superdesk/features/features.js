(function() {
'use strict';

Features.$inject = ['urls'];
function Features(urls) {
    urls.links().then(angular.bind(this, function(links) {
        angular.extend(this, links);
    }));
}

/**
 * Provides info what features are available on server
 */
angular.module('superdesk.features', ['superdesk.api'])
    .service('features', Features);

})();
