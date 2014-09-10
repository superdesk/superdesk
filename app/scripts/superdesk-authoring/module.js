define([
    'angular'
], function(angular) {
    'use strict';

    LockService.$inject = ['$q', 'api', 'session'];
    function LockService($q, api, session) {

        /**
         * Lock an item
         */
        this.lock = function(item) {
            if (this.isLocked(item)) {
                return $q.reject();
            } else {
                return api('archive_lock', item).save({});
            }
        };

        /**
         * Unlock an item
         */
        this.unlock = function(item) {
            return api('archive_unlock', item).save({});
        };

        /**
         * Test if an item is locked
         */
        this.isLocked = function(item) {
            return item && item.lock_user && item.lock_user !== session.identity._id;
        };
    }

    ConfirmDirtyFactory.$inject = ['$window', '$q', 'modal', 'gettext'];
    function ConfirmDirtyFactory($window, $q, modal, gettext) {
        /**
         * Asks for user confirmation if there are some changes which are not saved.
         * - Detecting changes via $scope.dirty - it's up to the controller to set it.
         */
        return function ConfirmDirty($scope) {
            $window.onbeforeunload = function() {
                if ($scope.dirty) {
                    return gettext('There are unsaved changes. If you navigate away, your changes will be lost.');
                }
            };

            $scope.$on('$destroy', function() {
                $window.onbeforeunload = angular.noop;
            });

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
        '$interval',
        '$timeout',
        'superdesk',
        'api',
        'workqueue',
        'notify',
        'gettext',
        'ConfirmDirty',
        'lock'
    ];

    function AuthoringController($scope, $routeParams, $interval, $timeout, superdesk, api,
        workqueue, notify, gettext, ConfirmDirty, lock) {
        var _item,
            _autosaveFlag,
            confirm = new ConfirmDirty($scope);

        $scope.item = null;
        $scope.dirty = null;
        $scope.workqueue = workqueue.all();
        $scope.editable = false;
        $scope.currentVersion = null;
        setupNewItem();
        $scope.saving = false;
        $scope.saved = false;

        function setupNewItem() {
            if ($routeParams._id) {
                _item = workqueue.find({_id: $routeParams._id}) || workqueue.active;
                lock.lock(_item)['finally'](function() {
                    $scope.item = _.create(_item);
                    $scope.editable = !lock.isLocked(_item);
                    workqueue.setActive(_item);
                });
            }
        }

        function isEditable(item) {
            if ($scope.isLocked(item)) {
                return false;
            }

            if (!angular.isDefined(item._latest_version)) {
                return true;
            }

            return item._latest_version === item._version;
        }

        function isDirty(item) {
            var dirty = false;
            angular.forEach(item, function(val, key) {
                dirty = dirty || val !== _item[key];
            });

            return dirty;
        }

        function stopAutosaving() {
            if (angular.isDefined(_autosaveFlag)) {
                $interval.cancel(_autosaveFlag);
                _autosaveFlag = undefined;
            }
        }

        $scope.$watchCollection('item', function(item) {
            if (!item) {
                $scope.dirty = $scope.editable = false;
                return;
            }

            $scope.editable = isEditable(item);
            $scope.dirty = isDirty(item);

            if ($scope.dirty) {
                if ($scope.editable && !angular.isDefined(_autosaveFlag)) {
                    _autosaveFlag = $interval($scope.update, 5000);
                }
            } else {
                stopAutosaving();
            }
        });

        $scope.isLocked = function(item) {
            return lock.isLocked(item);
        };

        $scope.articleSwitch = function() {
            $scope.update();
            stopAutosaving();
        };

        $scope.update = function() {
            if ($scope.dirty && $scope.editable) {
                workqueue.update($scope.item); //do local update
                $scope.saving = true;
                api('autosave', $scope.item).save({}, $scope.item).then(function() {
                    $scope.saving = false;
                    $scope.saved = true;
                    $timeout(function() {
                        $scope.saved = false;
                    }, 2000);
                    console.log('success autosave');
                }, function(response) {
                    console.log('error on autosave');
                    console.log(response);
                });
            }
        };

    	$scope.save = function() {
            delete $scope.item._version;
    		return api.archive.save(_item, $scope.item).then(function(res) {
                workqueue.update(_item);
                $scope.item = _.create(_item);
                $scope.dirty = false;
                notify.success(gettext('Item updated.'));
    		}, function(response) {
    			notify.error(gettext('Error. Item not updated.'));
    		});
    	};

        $scope.close = function() {
            confirm.confirm().then(function() {
                if ($scope.editable) {
                    lock.unlock($scope.item);
                }
                $scope.dirty = false;
                workqueue.remove($scope.item);
                superdesk.intent('author', 'dashboard');
            });
        };

        $scope.$on('$routeUpdate', setupNewItem);
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

    WorkqueueCtrl.$inject = ['$scope', 'workqueue', 'superdesk', 'ContentCtrl'];
    function WorkqueueCtrl($scope, workqueue, superdesk, ContentCtrl) {
        $scope.workqueue = workqueue.all();
        $scope.content = new ContentCtrl();

        $scope.openItem = function(article) {
            if ($scope.active) {
                $scope.update();
            }
            workqueue.setActive(article);
            superdesk.intent('author', 'article', article);
        };

        $scope.openDashboard = function() {
            superdesk.intent('author', 'dashboard');
        };

        $scope.closeItem = function(item) {
            if ($scope.active) {
                $scope.close();
            } else {
                workqueue.remove(item);
                superdesk.intent('author', 'dashboard');
            }
        };
    }

    function WorkqueueListDirective() {
        return {
            templateUrl: 'scripts/superdesk-authoring/views/opened-articles.html',
            scope: {
                active: '=',
                update: '&',
                close: '&'
            },
            controller: WorkqueueCtrl
        };
    }

    return angular.module('superdesk.authoring', [
            'superdesk.editor',
            'superdesk.authoring.widgets',
            'superdesk.authoring.metadata',
            'superdesk.authoring.comments',
            'superdesk.authoring.versions'
        ])

        .service('lock', LockService)
    	.service('workqueue', WorkqueueService)
        .factory('ConfirmDirty', ConfirmDirtyFactory)
        .directive('sdWorkqueue', WorkqueueListDirective)

        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/authoring/:_id', {
                	label: gettext('Authoring'),
	                templateUrl: 'scripts/superdesk-authoring/views/main.html',
                    topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
	                controller: AuthoringController,
	                beta: true,
	                filters: [{action: 'author', type: 'article'}]
	            })
                .activity('/authoring/', {
                    label: gettext('Authoring'),
                    templateUrl: 'scripts/superdesk-authoring/views/dashboard.html',
                    topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
                    beta: true,
                    controller: WorkqueueCtrl,
                    category: superdesk.MENU_MAIN,
                    filters: [{action: 'author', type: 'dashboard'}]
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
