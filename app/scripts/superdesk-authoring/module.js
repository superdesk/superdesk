define([
    'angular'
], function(angular) {
    'use strict';

    ConfirmDirtyFactory.$inject = ['$window', '$location', '$q', 'modal', 'gettext'];
    function ConfirmDirtyFactory($window, $location, $q, modal, gettext) {
        /**
         * Asks for user confirmation if there are some changes which are not saved.
         * - Detecting changes via $scope.dirty - it's up to the controller to set it.
         */
        return function ConfirmDirty($scope) {
            var confirmed = false;

            $scope.$on('$locationChangeStart', function(e, next) {
                if ($scope.dirty && !confirmed) {
                    e.preventDefault();
                    confirmDirty().then(function() {
                        confirmed = true;
                        $location.url(next.split('#')[1]);
                    });
                }
            });

            $scope.$on('$routeUpdate', function() {
                confirmed = false;
            });

            $window.onbeforeunload = function() {
                if ($scope.dirty) {
                    return gettext('There are unsaved changes. If you navigate away, your changes will be lost.');
                }
            };

            this.confirm = function() {
                if ($scope.dirty) {
                    return confirmDirty();
                } else {
                    return $q.when();
                }
            };

            function confirmDirty() {
                return modal.confirm(gettext('There are unsaved changes. Please confirm you want to close the article without saving.'));
            }
        };
    }

    AuthoringController.$inject = [
        '$scope',
        '$routeParams',
        'superdesk',
        'api',
        'workqueue',
        'notify',
        'gettext',
        'ConfirmDirty'
    ];

    function AuthoringController($scope, $routeParams, superdesk, api, workqueue, notify, gettext, ConfirmDirty) {
        var _item;
        $scope.item = null;
        $scope.dirty = null;
        $scope.workqueue = workqueue.all();
        setupNewItem();

        var confirm = new ConfirmDirty($scope);

        function setupNewItem() {
            var _id = $routeParams._id;
            if (_id) {
                _item = workqueue.find({_id: _id}) || workqueue.active;
                $scope.item = _.create(_item);
                workqueue.setActive(_item);
            }
        }

        $scope.$watch('item', function(item, oldItem) {
            if (item === oldItem) {
                $scope.dirty = false;
                return;
            }

            $scope.dirty = item && oldItem && item._id === oldItem._id;
        }, true);

        $scope.switchArticle = function(article) {
            workqueue.update($scope.item);
            workqueue.setActive(article);
            superdesk.intent('author', 'article', article);
        };

    	$scope.save = function() {
    		api.archive.save(_item, $scope.item).then(function(res) {
                workqueue.update($scope.item);
                notify.success(gettext('Item updated.'));
                $scope.dirty = false;
    		}, function(response) {
    			notify.error(gettext('Error. Item not updated.'));
    		});
    	};

        $scope.close = function() {
            confirm.confirm().then(function() {
                superdesk.intent('view', 'content');
            });
        };

        $scope.$on('$routeUpdate', setupNewItem);
    }

    VersioningController.$inject = ['$scope', 'api', '$location', 'notify', 'workqueue'];
    function VersioningController($scope, api, $location, notify, workqueue) {
        $scope.item = null;
        $scope.versions = null;
        $scope.selected = null;
        $scope.users = {};

        $scope.$watch(function() {
            return $location.search()._id;
        }, function(_id) {
            $scope.item = null;
            $scope.versions = null;

            if (_id) {
                fetchItem(_id);
            }
        });

        var fetchUser = function(id) {
            api.users.getById(id)
            .then(function(result) {
                $scope.users[id] = result;
            });
        };

        var fetchItem = function(id) {
            id = id || $scope.item._id;
            return api.archive.getById(id)
            .then(function(result) {
                $scope.item = result;
                return fetchVersions();
            });
        };

        var fetchVersions = function() {
            $scope.users = {};
            return api.archive.getByUrl($scope.item._links.self.href + '?version=all&embedded={"user":1}')
            .then(function(result) {
                _.each(result._items, function(version) {
                    var creator = version.creator || version.original_creator;
                    if (creator && !$scope.users[creator]) {
                        fetchUser(creator);
                    }
                });
                $scope.versions = result;
                $scope.selected = _.find($scope.versions._items, {_version: $scope.item._latest_version});
            });
        };

        $scope.revert = function(version) {
            api.archive.replace($scope.item._links.self.href, {
                type: 'text',
                last_version: $scope.item._version,
                old_version: version
            })
            .then(function(result) {
                notify.success(gettext('Item reverted.'));
                fetchItem()
                .then(function() {
                    workqueue.update($scope.item);
                });
            }, function(result) {
                notify.error(gettext('Error. Item not reverted.'));
            });
        };
    }

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
            if (!item) {
                this.active = null;
            } else {
                this.active = this.find({_id: item._id});
            }
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

    return angular.module('superdesk.authoring', [
            'superdesk.editor',
            'superdesk.authoring.widgets',
            'superdesk.authoring.comments'
        ])

    	.service('workqueue', WorkqueueService)
        .factory('ConfirmDirty', ConfirmDirtyFactory)

        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/authoring/:_id', {
                	label: gettext('Authoring'),
	                templateUrl: 'scripts/superdesk-authoring/views/main.html',
                    topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
	                controller: AuthoringController,
	                category: superdesk.MENU_MAIN,
	                beta: true,
	                filters: [{action: 'author', type: 'article'}]
	            })
	            .activity('/versions/', {
                	label: gettext('Authoring - item versions'),
	                templateUrl: 'scripts/superdesk-authoring/views/versions.html',
	                controller: VersioningController,
	                beta: true,
	                filters: [{action: 'versions', type: 'author'}]
	            })
	            .activity('edit.text', {
	            	label: gettext('Edit item'),
	            	icon: 'pencil',
	            	controller: ['data', '$location', 'workqueue', 'superdesk', function(data, $location, workqueue, superdesk) {
	            		workqueue.add(data.item);
                        superdesk.intent('author', 'article', data.item);
	                }],
	            	filters: [
	                    {action: superdesk.ACTION_EDIT, type: 'archive'}
	                ]
	            });
        }]);
});
