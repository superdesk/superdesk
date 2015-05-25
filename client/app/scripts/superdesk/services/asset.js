(function() {
'use strict';

/**
 * Asset module
 *
 * This module provides urls for static assets.
 */
return angular.module('superdesk.asset', ['superdesk.config'])
    .provider('asset', [ '$injector', function ($injector) {
        this.templateUrl = function(path) {
            var config = $injector.get('config'),
                ret = path;
            if (!/^(https?:\/\/|\/\/|\/|.\/|..\/)/.test(path)) {
                ret = 'scripts/' + ret;
            }
            if (!/^(https?:\/\/|\/\/)/.test(path) && config.paths && config.paths.superdesk) {
                ret = config.paths.superdesk + ret;
            }
            ret = ret.replace(/[^\/]+\/+\.\.\//g, '')
                     .replace(/\.\//g, '')
                     .replace(/(\w)\/\/(\w)/g, '$1/$2');
            return ret;
        };

        this.imageUrl = this.templateUrl;

        this.$get = function() {
            return this;
        };
    }]);
})();
