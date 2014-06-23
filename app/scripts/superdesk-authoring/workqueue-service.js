define(['lodash', 'angular'], function(_, angular) {
    'use strict';

    WorkqueueService.$inject = ['storage'];
    function WorkqueueService(storage) {
        /**
         * Set items for further work, in next step of the workflow.
         */

        var queue = storage.getItem('workqueue:items') || [];
        this.length = 0;
        this.active = null;

        /**
         * Add an item into queue
         *
         * it checks if item is in queue already and if yes it will move it to the very end
         *
         * @param {Object} item
         */
        this.add = function(item) {
            _.remove(queue, {_id: item._id});
            queue.unshift(item);
            this.length = queue.length;
            this.active = item;
            this.save();
            return this;
        };

        /**
         * Update item in a queue
         */
        this.update = function(item) {
            if (item) {
                var base = this.find({_id: item._id});
                queue[_.indexOf(queue, base)] = _.extend(base, item);
                this.save();
            }
        };

        /**
         * Get first item
         */
        this.first = function() {
            return _.first(queue);
        };

        /**
         * Get all items from queue
         */
        this.all = function() {
            return queue;
        };

        /**
         * Save queue to local storage
         */
        this.save = function() {
            storage.setItem('workqueue:items', queue);
        };

        /**
         * Find item by given criteria
         */
        this.find = function(criteria) {
            return _.find(queue, criteria);
        };

        /**
         * Set given item as active
         */
        this.setActive = function(item) {
            this.active = this.find({_id: item._id});
        };

        /**
         * Get '_id' of active item or null if it's not defined
         */
        this.getActive = function() {
            return this.active ? this.active._id : null;
        };

        /**
         * Remove given item from queue
         */
        this.remove = function(item) {
            _.remove(queue, {_id: item._id});
            this.length = queue.length;
            this.save();

            if (this.active._id === item._id && this.length > 0) {
                this.setActive(_.first(queue));
            } else {
                this.active = null;
            }
        };

    }

    return WorkqueueService;
});
