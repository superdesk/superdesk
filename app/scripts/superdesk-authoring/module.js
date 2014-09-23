define([
    'angular'
], function(angular) {
    'use strict';

    /**
     * Extend content of dest
     *
     * @param {Object} dest
     * @param {Object} src
     */
    function extendItem(dest, src) {
        angular.extend(dest, {
            headline: src.headline || '',
            slugline: src.slugline || '',
            body_html: src.body_html || ''
        });
    }

    AutosaveService.$inject = ['$q', '$timeout', 'api'];
    function AutosaveService($q, $timeout, api) {
        var RESOURCE = 'archive_autosave',
            AUTOSAVE_TIMEOUT = 3000,
            _timeout;

        /**
         * Open an item
         */
        this.open = function(item) {
            if (item._locked) {
                // no way to get autosave
                return $q.when(item);
            }

            return api(RESOURCE).getById(item._id).then(function(autosave) {
                extendItem(item, autosave);
                item._autosave = autosave;
                return item;
            }, function(err) {
                return item;
            });
        };

        /**
         * Autosave an item
         */
        this.save = function(item) {
            $timeout.cancel(_timeout);
            _timeout = $timeout(function() {
                var data = {_id: item._id, guid: item.guid};
                extendItem(data, item);
                return api(RESOURCE).save(data).then(function(autosave) {
                    item._autosave = autosave;
                });
            }, AUTOSAVE_TIMEOUT);
            return _timeout;
        };

        /**
         * Drop autosave
         */
        this.drop = function(item) {
            $timeout.cancel(_timeout);
            api(RESOURCE).remove(item._autosave);
            item._autosave = null;
        };
    }

    ItemLoader.$inject = ['$route', 'api', 'lock', 'autosave', 'workqueue'];
    function ItemLoader($route, api, lock, autosave, workqueue) {
        console.time('item');
        return api('archive').getById($route.current.params._id).then(function(item) {
            console.time('lock');
            return item;
            // TODO(petr): enable lock once autosaved is fixed
            // return lock.lock(item);
        }).then(function(item) {
            console.timeEnd('lock');
            console.time('autosave');
            return autosave.open(item);
        }).then(function(item) {
            workqueue.setActive(item);
            console.timeEnd('lock');
            console.timeEnd('autosave');
            console.timeEnd('item');
            return item;
        });
    }

    LockService.$inject = ['$q', 'api', 'session'];
    function LockService($q, api, session) {

        /**
         * Lock an item
         */
        this.lock = function(item) {
            return api('archive_lock', item).save({}).then(function(lock) {
                item._locked = false;
                return item;
            }, function(err) {
                item._locked = true;
                return item;
            });
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
            if ('_locked' in item) {
                return item._locked;
            }

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
        '$q',
        'superdesk',
        'api',
        'workqueue',
        'notify',
        'gettext',
        'ConfirmDirty',
        'lock',
        'desks',
        'item',
        'autosave'
    ];

    function AuthoringController($scope, $q, superdesk, api, workqueue, notify, gettext, ConfirmDirty, lock, desks, item, autosave) {
        var confirm = new ConfirmDirty($scope),
            stopWatch = angular.noop;

        $scope.workqueue = workqueue.all();
        $scope.saving = false;
        $scope.saved = false;
        $scope.dirty = null;
        $scope.sendTo = false;
        $scope.stages = null;

        function startWatch() {
            function isDirty() {
                var dirty = false;
                angular.forEach($scope.item, function(val, key) {
                    dirty = dirty || val !== item[key];
                });

                return dirty;
            }

            stopWatch(); // stop watch if any
            stopWatch = $scope.$watchCollection('item', function(item) {
                $scope.dirty = isDirty();
                if ($scope.dirty && $scope.isEditable()) {
                    $scope.saving = true;
                    autosave.save($scope.item).then(function() {
                        $scope.saving = false;
                    });
                }
            });
        }

        desks.initialize()
        .then(function() {
            api('stages').query({where: {desk: $scope.item.task.desk}})
            .then(function(result) {
                $scope.stages = result;
            });
        });

        $scope.isLocked = function(item) {
            return lock.isLocked(item);
        };

        $scope.isEditable = function() {
            return !$scope._preview && !item._locked;
        };

        /**
         * Create a new version
         */
    	$scope.save = function() {
            stopWatch();
    		return api.archive.save(item, $scope.item).then(function(res) {
                item._autosave = null;
                workqueue.update(item);
                $scope.item = _.create(item);
                $scope.dirty = false;
                notify.success(gettext('Item updated.'));
                startWatch();
                return item;
    		}, function(response) {
    			notify.error(gettext('Error. Item not updated.'));
    		});
    	};

        /**
         * Close an item - unlock and remove from workqueue
         */
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

        /**
         * Preview different version of an item
         */
        $scope.preview = function(version) {
            stopWatch();
            extendItem($scope.item, version);
            $scope._preview = true;
            $scope._editable = false;
        };

        /**
         * Revert item to given version
         */
        $scope.revert = function(version) {
            extendItem($scope.item, version);
            return $scope.save();
        };

        /**
         * Close preview and start working again
         */
        $scope.closePreview = function() {
            $scope._preview = false;
            $scope._editable = $scope.isEditable();
            $scope.item = _.create(item);
            startWatch();
        };

        /**
         * Drop autosave
         */
        $scope.dropAutosave = function(version) {
            autosave.drop(item);
            extendItem(item, version);
        };

        if ($scope.isEditable()) {
            // start autosaving
            $scope.closePreview();
        }
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
        .service('autosave', AutosaveService)
        .factory('ConfirmDirty', ConfirmDirtyFactory)
        .directive('sdDashboardCard', DashboardCard)

        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/authoring/:_id', {
                	label: gettext('Authoring'),
	                templateUrl: 'scripts/superdesk-authoring/views/authoring.html',
                    topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
	                controller: AuthoringController,
	                beta: true,
	                filters: [{action: 'author', type: 'article'}],
                    resolve: {item: ItemLoader}
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
