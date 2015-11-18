define(['lodash'], function(_) {
    'use strict';

    return ['$q', 'storage', 'api', 'preferencesService', 'notify',
    function($q, storage, api, preferencesService, notify) {
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

            var update = {
                'scratchpad:items': this.itemList
            };

            var instance = this;

            preferencesService.update(update, 'scratchpad:items').then(function() {
                    instance.update();
                }, function(response) {
                    notify.error(gettext('User preference could not be saved...'));
                });
        };
        this.loadItemList = function() {
            var instance = this;
            return preferencesService.get('scratchpad:items').then(function(result) {
                if (result) {
                    instance.itemList = result;
                }
                return result;
            });
        };

        this.addItem = function(item) {
            this.itemList = _.without(this.itemList, item._links.self.href);
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
            var promises = [];

            _.forEach(this.itemList, function(href) {
                if (!self.data[href]) {
                    promises.push(api.archive.getByUrl(href));
                }
            });

            return $q.all(promises).then(function(response) {
                _.forEach(response, function(item) {
                    self.data[item._links.self.href] = item;
                });
                var items = [];
                _.forEach(self.itemList, function(href) {
                    items.push(self.data[href]);
                });
                return items;
            });

        };
    }];
});
