(function() {
    'use strict';

    var CONTENT_FIELDS = ['headline', 'slugline', 'body_html'];

    /**
     * Extend content of dest
     *
     * @param {Object} dest
     * @param {Object} src
     */
    function extendItem(dest, src) {
        angular.extend(dest, _.pick(src, CONTENT_FIELDS));
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

            return api.find(RESOURCE, item._id).then(function(autosave) {
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
        this.save = function(item, data) {
            $timeout.cancel(_timeout);
            _timeout = $timeout(function() {
                var diff = angular.extend({_id: item._id}, data);
                return api.save(RESOURCE, {}, diff).then(function(_autosave) {
                    item._autosave = _autosave;
                    extendItem(item._autosave, data);
                    extendItem(item, data);
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
        return api.find('archive', $route.current.params._id).then(function(item) {
            console.time('lock');
            return lock.lock(item);
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
            if (!item.lock_user) {
                return api('archive_lock', item).save({}).then(function(lock) {
                    item._locked = false;
                    item.lock_user = session.identity.id;
                    item.lock_session = session.sessionId;
                    return item;
                }, function(err) {
                    item._locked = true;
                    return item;
                });
            } else {
                item._locked = (item.lock_user !== session.identity._id || item.lock_session !== session.sessionId);
                return $q.when(item);
            }
        };

        /**
         * Unlock an item
         */
        this.unlock = function(item) {
            return api('archive_unlock', item).save({});
        };

        /**
         * Test if an item is locked for me
         */
        this.isLocked = function(item) {
            return item.lock_user && item.lock_session &&
                (item.lock_user !== session.identity._id || item.lock_session !== session.sessionId);
        };

        /**
        * Test is an item is locked by me in another session
        */
        this.isLockedByMe = function(item) {
            return item.lock_user && item.lock_session &&
                (item.lock_user === session.identity._id && item.lock_session !== session.sessionId);
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
        'superdesk',
        'api',
        'workqueue',
        'notify',
        'gettext',
        'lock',
        'desks',
        'item',
        'autosave'
    ];

    function AuthoringController($scope, superdesk, api, workqueue, notify, gettext, lock, desks, item, autosave) {
        var stopWatch = angular.noop;

        $scope.workqueue = workqueue.all();
        $scope.saving = false;
        $scope.saved = false;
        $scope.dirty = false;
        $scope.viewSendTo = false;

        function startWatch() {
            function isDirty() {
                var dirty = false;
                angular.forEach($scope.item, function(val, key) {
                    dirty = dirty || val !== item[key];
                });

                return dirty;
            }

            stopWatch(); // stop watch if any
            stopWatch = $scope.$watchGroup([
                'item.headline',
                'item.slugline',
                'item.body_html'
            ], function(changes) {
                $scope.dirty = isDirty();
                if ($scope.dirty && $scope.isEditable()) {
                    $scope.saving = true;
                    autosave.save(item, $scope.item).then(function() {
                        $scope.saving = false;
                    });
                }
            });
        }

        $scope.isEditable = function() {
            return !$scope._preview && !$scope.item._locked;
        };

        /**
         * Create a new version
         */
    	$scope.save = function() {
            stopWatch();
    		return api.save('archive', item, $scope.item).then(function(res) {
                workqueue.update(item);
                item._autosave = null;
                $scope.dirty = false;
                $scope.item = _.create(item);
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
            if ($scope._editable) {
                lock.unlock($scope.item);
            }
            $scope.dirty = false;
            workqueue.remove($scope.item);
            superdesk.intent('author', 'dashboard');
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
            $scope.item = _.create(item);
            extendItem($scope.item, item._autosave || {});
            $scope._preview = false;
            $scope._editable = $scope.isEditable();
            if ($scope._editable) {
                startWatch();
            }
        };

        /**
         * Drop autosave
         */
        $scope.dropAutosave = function(version) {
            autosave.drop(item);
            extendItem(item, version);
        };

        // init
        $scope.closePreview();
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

    SendItem.$inject = ['superdesk', 'api', 'desks', 'notify'];
    function SendItem(superdesk, api, desks, notify) {
        return {
            scope: {
                item: '=',
                view: '='
            },
            templateUrl: 'scripts/superdesk-authoring/views/send-item.html',
            link: function sendItemLink(scope, elem, attrs) {
                scope.desk = null;
                scope.desks = null;
                scope.stages = null;

                scope.$watch('item', function fetchDesks() {
                    if (scope.item.task && scope.item.task.desk) {

                        api.find('tasks', scope.item._id).then(function(_task) {
                            scope.task = _task;
                        });

                        desks.initialize()
                        .then(function fetchStages() {
                            scope.desks = desks.desks;
                            scope.desk = desks.deskLookup[scope.item.task.desk];
                            if (scope.desk) {
                                api('stages').query({where: {desk: scope.desk._id}})
                                .then(function(result) {
                                    scope.stages = result;
                                });
                            }
                        });
                    }
                });

                scope.sendToDesk = function sendToDesk(desk) {
                    save({task: _.extend(
                        scope.task.task,
                        {desk: desk._id, stage: desk.incoming_stage || null}
                    )});
                };

                scope.sendToStage = function sendToStage(stage) {
                    save({task: _.extend(
                        scope.task.task,
                        {stage: stage._id}
                    )});
                };

                function save(data) {
                    api.save('tasks', scope.task, data).then(gotoDashboard);
                }

                function gotoDashboard() {
                    notify.success(gettext('Item sent.'));
                    superdesk.intent('author', 'dashboard');
                }
            }
        };
    }

    return angular.module('superdesk.authoring', [
            'superdesk.editor',
            'superdesk.activity',
            'superdesk.authoring.widgets',
            'superdesk.authoring.metadata',
            'superdesk.authoring.comments',
            'superdesk.authoring.versions',
            'superdesk.authoring.workqueue',
            'superdesk.desks'
        ])

        .service('lock', LockService)
        .service('autosave', AutosaveService)
        .factory('ConfirmDirty', ConfirmDirtyFactory)
        .directive('sdDashboardCard', DashboardCard)
        .directive('sdSendItem', SendItem)

        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('authoring', {
                    when: '/authoring/:_id',
                	label: gettext('Authoring'),
	                templateUrl: 'scripts/superdesk-authoring/views/authoring.html',
                    topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
	                controller: AuthoringController,
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
})();
