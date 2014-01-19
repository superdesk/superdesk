define(['lodash', 'angular'], function(_, angular) {
    'use strict';

    angular.module('superdesk.items.services', [])
        .service('panesService', ['storage', 'superdesk', function(storage, superdesk) {
            var paneKey = 'aes:panes';

            this.load = function() {
                var userPanes = storage.getItem(paneKey) || {};
                
                angular.forEach(superdesk.panes, function(userPane, key) {
                    userPanes[key] = angular.extend({}, userPane, userPanes[key]);
                });

                return userPanes;
            };

            this.save = function(userPanes) {
                var config = {};

                angular.forEach(userPanes, function(pane, key) {
                    config[key] = _.pick(pane, ['order', 'position','active','selected']);
                });

                storage.setItem(paneKey, config, true);
            };

            this.changePosition = function(key,position) {
                var userPanes = this.load();
                userPanes[key].position = angular.extend(userPanes[key].position, position);
                this.save(userPanes);
            };

        }]);
});