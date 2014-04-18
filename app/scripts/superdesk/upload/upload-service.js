define([], function() {
    'use strict';

    UploadService.$inject = ['$q', '$rootScope'];
    function UploadService($q, $rootScope) {
        /**
         * Start upload workflow
         *
         * @param {string} base
         * @return {object} promise
         */
        this.upload = function(base) {
            this.delay = $q.defer();
            $rootScope.$broadcast('upload:show');
            return this.delay.promise;
        };
    }

    return UploadService;
});
