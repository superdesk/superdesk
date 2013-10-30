define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.services.notify', [])
        .service('notify', ['$timeout', function ($timeout) {
            function NotifyService() {
                this.messages = [];

                this.pop = function() {
                    return this.messages.pop();
                };

                this.addMessage = function(type, text, ttl) {
                    var self = this;
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
        .directive('sdNotify', function (notify) {
            return {
                scope: {},
                templateUrl: 'scripts/superdesk/views/notify.html',
                link: function (scope, element, items) {
                    scope.messages = notify.messages;
                }
            };
        });
});