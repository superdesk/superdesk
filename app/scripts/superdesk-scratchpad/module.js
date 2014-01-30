define([
    'angular',
    'lodash'
], function(angular, _) {
    'use strict';

    var app = angular.module('superdesk.scratchpad', []);
    app.service('scratchpadService', ['$q', 'storage', 'server', function($q, storage, server) {
        this.listeners = [];
        this.save = function() {
            storage.setItem('scratchpad:items', this.items, true);
            this.update();
        };
        this.load = function() {
            this.items = storage.getItem('scratchpad:items');
            if (!this.items) {
                this.items = [];
                this.save();
            }
            this.update();
        };
        this.getItems = function() {
            return this.items;
        };
        this.getItemsResolved = function() {
            var delay = $q.defer();

            var promises = [];
            _.forEach(this.items, function(item) {
                promises.push(server._http('get', server._wrapUrl(item)));
            });

            $q.all(promises).then(function(response) {
                delay.resolve(response);
            });

            return delay.promise;
        };
        this.addItem = function(item) {
            this.removeItem(item);
            this.items.push(item._links.self.href);
            this.save();
        };
        this.removeItem = function(item) {
            this.items = _.without(this.items, item._links.self.href);
            this.save();
        };
        this.checkItemExists = function(item) {
            return (this.items.indexOf(item._links.self.href) !== -1);
        };
        this.sort = function(newSort) {
            var self = this;
            var items = [];
            _.forEach(newSort, function(index) {
                items.push(self.items[index]);
            });
            this.items = items;
            this.save();
        };
        this.addListener = function(listener) {
            this.listeners.push(listener);
        };
        this.update = function() {
            _.forEach(this.listeners, function(listener) {
                listener();
            });
        };

        this.load();
    }]);
    app.directive('sdScratchpadAdd', ['scratchpadService', function(scratchpadService) {
        return {
            replace: true,
            templateUrl: 'scripts/superdesk-scratchpad/views/scratchpadAdd.html',
            scope: {
                scratchpadItem: '='
            },
            link: function(scope, element, attrs) {
                scope.check = function() {
                    if (scope.scratchpadItem === null) {
                        return false;
                    }
                    return scratchpadService.checkItemExists(scope.scratchpadItem);
                };

                scope.addRemove = function() {
                    return (scope.check()) ? scope.remove() : scope.add();
                };

                scope.add = function() {
                    return scratchpadService.addItem(scope.scratchpadItem);
                };

                scope.remove = function() {
                    return scratchpadService.removeItem(scope.scratchpadItem);
                };
            }
        };
    }]);
    app.directive('sdScratchpad', ['scratchpadService', function(scratchpadService){
        return {
            templateUrl: 'scripts/superdesk-scratchpad/views/scratchpad.html',
            replace: true,
            link: function(scope, element, attrs) {
                scope.status = false;
                scope.update = function() {
                    scratchpadService.getItemsResolved().then(function(items) {
                        scope.items = items;
                    });
                };
                scope.sort = function() {
                    var newSort = _.pluck(_.pluck(element.find('div[data-index]'), 'dataset'), 'index');
                    console.log(newSort);
                    scratchpadService.sort(newSort);
                };
                scope.drop = function(item) {
                    if (item) {
                        scratchpadService.addItem(item);
                    }
                };

                scratchpadService.addListener(function() {
                    scope.update();
                });
                scope.update();
            }
        };
    }]);
});
