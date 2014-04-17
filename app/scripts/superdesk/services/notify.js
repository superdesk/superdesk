define(['angular'], function(angular) {
    'use strict';

    return angular.module('superdesk.notify', [])
        .service('notify', ['$timeout', function ($timeout) {
            function NotifyService() {

                var ttls = {
                    info: 3000,
                    success: 3000,
                    error: 5000
                };

                this.messages = [];

                this.pop = function() {
                    return this.messages.pop();
                };

                this.addMessage = function(type, text, ttl) {
                    var self = this;

                    if (ttl == null) {
                        ttl = ttls[type];
                    }

                    this.messages.push({type: type, msg: text});
                    if (ttl) {
                        $timeout(function() {
                            self.pop();
                        }, ttl);
                    }
                };

                angular.forEach(['info', 'success', 'error'], function(type) {
                    var self = this;
                    this[type] = function(text, ttl) {
                        self.addMessage(type, text, ttl);
                    };
                }, this);
            }

            return new NotifyService();
        }])
        .directive('sdNotify', ['notify', function (notify) {
            return {
                scope: {},
                templateUrl: 'scripts/superdesk/views/notify.html',
                link: function (scope, element, items) {
                    scope.messages = notify.messages;
                }
            };
        }]);
});
