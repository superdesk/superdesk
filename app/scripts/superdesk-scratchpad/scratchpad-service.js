define(['lodash'], function(_) {
    'use strict';

    return ['$q', 'storage', 'server', function($q, storage, server) {
        this.listeners = [];
        this.data = {};
        this.itemList = [];

        this.addListener = function(listener) {
            this.listeners.push(listener);
        };
        this.update = function() {
            _.forEach(this.listeners, function(listener) {
                listener();
            });
        };
        this.saveItemList = function() {
            storage.setItem('scratchpad:items', this.itemList, true);
            this.update();
        };
        this.loadItemList = function() {
            var itemList = storage.getItem('scratchpad:items');
            if (itemList) {
                this.itemList = itemList;
                this.update();
            }
        };
        this.addItem = function(item) {
            this.removeItem(item);
            this.itemList.push(item._links.self.href);
            this.data[item._links.self.href] = item;
            this.saveItemList();
        };
        this.removeItem = function(item) {
            this.itemList = _.without(this.itemList, item._links.self.href);
            this.saveItemList();
        };
        this.checkItemExists = function(item) {
            return (this.itemList.indexOf(item._links.self.href) !== -1);
        };
        this.sort = function(newSort) {
            var self = this;
            var itemList = [];
            _.forEach(newSort, function(index) {
                itemList.push(self.itemList[index]);
            });
            this.itemList = itemList;
            this.saveItemList();
        };
        this.getItems = function() {
            var self = this;
            var delay = $q.defer();
            var promises = [];

            _.forEach(this.itemList, function(href) {
                if (!self.data[href]) {
                    promises.push(server._http('get', server._wrapUrl(href)));
                }
            });

            $q.all(promises).then(function(response) {
                _.forEach(response, function(item) {
                    self.data[item._links.self.href] = item;
                });
                var items = [];
                _.forEach(self.itemList, function(href) {
                    items.push(self.data[href]);
                });
                delay.resolve(items);
            });

            return delay.promise;
        };

        this.loadItemList();
    }];
});
