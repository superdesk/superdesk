define(['lodash', 'angular'], function(_, angular) {
    'use strict';

    angular.module('superdesk.users.providers', [])
        .factory('rolesLoader', ['$q', 'em', function ($q, em) {
            var delay = $q.defer();

            function zip(items, key) {
                var zipped = {};
                _.each(items, function(item) {
                    zipped[item[key]] = item;
                });

                return zipped;
            }

            em.repository('user_roles').all().then(function(data) {
                var roles = zip(data._items, '_id');
                delay.resolve(roles);
            });

            return delay.promise;
        }]);
});
