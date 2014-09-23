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
        '$timeout',
        'superdesk',
        'api',
        'workqueue',
        'notify',
        'gettext',
        'ConfirmDirty',
        'lock',
        '$q',
        'desks'
    ];

    function AuthoringController($scope, $routeParams, $timeout, superdesk,
            api, workqueue, notify, gettext, ConfirmDirty, lock, $q, desks) {
        var _item,
            confirm = new ConfirmDirty($scope);

        var AUTOSAVE_AFTER = 3000;

        $scope.item = null;
        $scope.dirty = null;
        $scope.workqueue = workqueue.all();
        $scope.editable = false;
        $scope.currentVersion = null;
        $scope.saving = false;
        $scope.saved = false;

        $scope.sendTo = false;
        $scope.stages = null;

        function setupNewItem() {
            if ($routeParams._id) {
                fetchNewItem().then(function() {
                    lock.lock(_item)['finally'](function() {
                        $scope.item = _.create(_item);
                        $scope.editable = !lock.isLocked(_item);
                        workqueue.setActive(_item);
                    });
                }, function(response) {
                    notify.error(gettext('Error. Item not found.'));
                });
            }
        }

        function fetchNewItem() {
            var d = $q.defer();
            _item = workqueue.find({_id: $routeParams._id});
            if (!_item) {
                api.archive.getById($routeParams._id)
                .then(function(item) {
                    workqueue.add(item);
                    _item = workqueue.active;
                    d.resolve();
                }, function(response) {
                    d.reject(response);
                });
            } else {
                d.resolve();
            }
            return d.promise;
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

        $scope.$watchCollection('item', function(item) {
            if (!item) {
                $scope.dirty = $scope.editable = false;
                return;
            }

            desks.initialize()
            .then(function() {
                api('stages').query({where: {desk: $scope.item.task.desk}})
                .then(function(result) {
                    $scope.stages = result;
                });
            });

            $scope.editable = isEditable(item);
            $scope.dirty = isDirty(item);

            if ($scope.dirty && $scope.editable) {
                $timeout(autosave, AUTOSAVE_AFTER);
            }
        });

        $scope.isLocked = function(item) {
            return lock.isLocked(item);
        };

        function autosave() {
            workqueue.update($scope.item); //do local update
            $scope.saving = true;
            api('autosave', $scope.item)
                .save({}, $scope.item)
                .then(function() {
                    $scope.saving = false;
                    $scope.saved = true;
                });
        }

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

        $scope.sendToStage = function(stage) {
            api('tasks').save(
                $scope.item,
                {task: _.extend(
                    $scope.item.task,
                    {stage: stage._id}
                )}
            )
            .then(function(result) {
                notify.success(gettext('Item sent.'));
                superdesk.intent('author', 'dashboard');
            });
        };

        $scope.$on('$routeUpdate', setupNewItem);
        setupNewItem();
    }

    function DashboardCard() {
        return {
            link: function(scope, elem) {
                var p = elem.parent();
                var maxW = p.parent().width();
                var marginW = parseInt(elem.css('margin-left'), 10) + parseInt(elem.css('margin-right'), 10);
                var newW = p.outerWidth() + elem.outerWidth() + marginW;
                if (newW < maxW) {
                    p.outerWidth(newW);
                }
            }
        };
    }

    return angular.module('superdesk.authoring', [
            'superdesk.editor',
            'superdesk.authoring.widgets',
            'superdesk.authoring.metadata',
            'superdesk.authoring.comments',
            'superdesk.authoring.versions',
            'superdesk.authoring.workqueue'
        ])

        .service('lock', LockService)
        .factory('ConfirmDirty', ConfirmDirtyFactory)
        .directive('sdDashboardCard', DashboardCard)

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
