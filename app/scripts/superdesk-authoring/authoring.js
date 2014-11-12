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
        this.open = function openAutosave(item) {
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
        this.save = function saveAutosave(item, data) {
            this.stop();
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
         * Stop pending autosave
         */
        this.stop = function stopAutosave() {
            if (_timeout) {
                $timeout.cancel(_timeout);
                _timeout = null;
            }
        };

        /**
         * Drop autosave
         */
        this.drop = function dropAutosave(item) {
            $timeout.cancel(_timeout);
            api(RESOURCE).remove(item._autosave);
            item._autosave = null;
        };
    }

    AuthoringService.$inject = ['$q', 'api', 'lock', 'autosave', 'workqueue', 'confirm'];
    function AuthoringService($q, api, lock, autosave, workqueue, confirm) {

        /**
         * Open an item for editing
         *
         * @param {string} _id Item _id.
         */
        this.open = function openAuthoring(_id) {
            return api.find('archive', _id, {embedded: {lock_user: 1}}).then(function _lock(item) {
                return lock.lock(item);
            }).then(function _autosave(item) {
                return autosave.open(item);
            }).then(function _workqueue(item) {
                workqueue.setActive(item);
                return item;
            });
        };

        /**
         * Close an item
         *
         * @param {Object} item Destination.
         * @param {Object} diff Changes.
         * @param {boolean} isDirty $scope dirty status.
         */
        this.close = function closeAuthoring(item, diff, isDirty) {
            if (isDirty && this.isEditable(item)) {
                return confirm.confirm()
                    .then(angular.bind(this, function save() {
                        return this.save(item, diff);
                    }), function() { // ignore saving
                        return $q.when();
                    })
                    .then(function unlock() {
                        return lock.unlock(item);
                    })
                    .then(function removeFromWorkqueue() {
                        return workqueue.remove(item);
                    });
            }

            return $q.when(workqueue.remove(item));
        };

        /**
         * Autosave the changes
         *
         * @param {Object} item Destination.
         * @param {Object} diff Changes.
         */
        this.autosave = function autosaveAuthoring(item, diff) {
            return autosave.save(item, diff);
        };

        /**
         * Save the item
         *
         * @param {Object} item Destination.
         * @param {Object} diff Changes.
         */
        this.save = function saveAuthoring(item, diff) {
            autosave.stop();
            return api.save('archive', item, diff).then(function(_item) {
                item._autosave = null;
                workqueue.update(item);
                return item;
            });
        };

        /**
         * Test if an item is editable
         *
         * @param {Object} item
         */
        this.isEditable = function isEditable(item) {
            return !!item.lock_user && !lock.isLocked(item);
        };

        /**
         * Unlock an item - callback for item:unlock event
         *
         * @param {Object} item
         * @param {string} userId
         */
        this.unlock = function unlock(item, userId) {
            autosave.stop();
            item.lock_user = null;
            confirm.unlock(userId);
        };
    }

    LockService.$inject = ['$q', 'api', 'session'];
    function LockService($q, api, session) {

        /**
         * Lock an item
         */
        this.lock = function lock(item) {
            if (!item.lock_user) {
                return api('archive_lock', item).save({}).then(function(lock) {
                    _.extend(item, lock);
                    item._locked = false;
                    item.lock_user = session.identity._id;
                    item.lock_session = session.sessionId;
                    return item;
                }, function(err) {
                    item._locked = true;
                    return item;
                });
            } else {
                item._locked = this.isLocked(item);
                return $q.when(item);
            }
        };

        /**
         * Unlock an item
         */
        this.unlock = function unlock(item) {
            return api('archive_unlock', item).save({}).then(function(lock) {
                _.extend(item, lock);
                item._locked = true;
                return item;
            }, function(err) {
                item._locked = true;
                return item;
            });
        };

        /**
         * Test if an item is locked, it can be locked by other user or you in different session.
         */
        this.isLocked = function isLocked(item) {
            var userId = item.lock_user && item.lock_user._id || item.lock_user;

            if (!userId) {
                return false;
            }

            if (userId !== session.identity._id) {
                return true;
            }

            if (!!item.lock_session && item.lock_session !== session.sessionId) {
                return true;
            }

            return false;
        };

        /**
        * Test is an item is locked by me in another session
        */
        this.isLockedByMe = function isLockedByMe(item) {
            return item.lock_user && item.lock_user === session.identity._id && item.lock_session !== session.sessionId;
        };
    }

    ConfirmDirtyService.$inject = ['$window', '$q', '$filter', 'api', 'modal', 'gettext'];
    function ConfirmDirtyService($window, $q, $filter, api, modal, gettext) {
        /**
         * Will ask for user confirmation for user confirmation if there are some changes which are not saved.
         * - Detecting changes via $scope.dirty - it's up to the controller to set it.
         */
        this.setupWindow = function setupWindow($scope) {
            $window.onbeforeunload = function() {
                if ($scope.dirty) {
                    return gettext('There are unsaved changes. If you navigate away, your changes will be lost.');
                }

                $scope.$on('$destroy', function() {
                    $window.onbeforeunload = angular.noop;
                });
            };
        };

        /**
         * In case $scope is dirty ask user if he want's to loose his changes.
         */
        this.confirm = function confirm() {
            return modal.confirm(
                gettext('There are some unsaved changes, do you want to save it now?'),
                gettext('Save changes?'),
                gettext('Save'),
                gettext('Ignore')
            );
        };

        /**
         * Make user aware that an item was unlocked
         *
         * @param {string} userId Id of user who unlocked an item.
         */
        this.unlock = function unlock(userId) {
            api.find('users', userId).then(function(user) {
                var msg = gettext('This item was unlocked by <b>{{ user }}</b>.').
                    replace('{{ user }}', $filter('username')(user));
                return modal.confirm(msg, gettext('Item Unlocked'), gettext('OK'), false);
            });
        };
    }

    AuthoringController.$inject = [
        '$scope',
        'superdesk',
        'workqueue',
        'notify',
        'gettext',
        'desks',
        'item',
        'authoring',
        'api'
    ];

    function AuthoringController($scope, superdesk, workqueue, notify, gettext, desks, item, authoring, api) {
        var stopWatch = angular.noop;

        $scope.workqueue = workqueue.all();
        $scope.dirty = false;
        $scope.viewSendTo = false;
        $scope.stage = null;

        if (item.task && item.task.stage) {
            api('stages').getById(item.task.stage)
            .then(function(result) {
                $scope.stage = result;
            });
        }

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
                if ($scope.dirty && authoring.isEditable(item)) {
                    authoring.autosave(item, $scope.item);
                }
            });
        }

        /**
         * Create a new version
         */
    	$scope.save = function() {
            stopWatch();
    		return authoring.save(item, $scope.item).then(function(res) {
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
            authoring.close(item, $scope.item, $scope.dirty).then(function() {
                superdesk.intent('author', 'dashboard');
            });
        };

        /**
         * Preview different version of an item
         */
        $scope.preview = function(version) {
            stopWatch();
            extendItem($scope.item, version);
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
            $scope._editable = authoring.isEditable(item);
            if ($scope._editable) {
                startWatch();
            }
        };

        // init
        $scope.closePreview();

        $scope.$on('item:unlock', function(_e, data) {
            if ($scope.item._id === data.item) {
                stopWatch();
                authoring.unlock(item, data.user);
                $scope._editable = false;
            }
        });
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

    SendItem.$inject = ['$q', 'superdesk', 'api', 'desks', 'notify'];
    function SendItem($q, superdesk, api, desks, notify) {
        return {
            scope: {
                item: '=',
                view: '=',
                _beforeSend: '=beforeSend'
            },
            templateUrl: 'scripts/superdesk-authoring/views/send-item.html',
            link: function sendItemLink(scope, elem, attrs) {
                scope.desk = null;
                scope.desks = null;
                scope.stages = null;

                scope.beforeSend = scope._beforeSend || $q.when;

                var fetchDesks = function() {
                    return api.find('tasks', scope.item._id)
                    .then(function(_task) {
                        scope.task = _task;
                    })
                    .then(function() {
                        desks.initialize()
                        .then(function() {
                            scope.desks = desks.desks;
                            if (scope.item.task && scope.item.task.desk) {
                                scope.desk = desks.deskLookup[scope.item.task.desk];
                            }
                        });
                    });
                };

                var fetchStages = function() {
                    desks.initialize()
                    .then(function() {
                        scope.desks = desks.desks;
                        if (scope.item.task && scope.item.task.desk) {
                            scope.desk = desks.deskLookup[scope.item.task.desk];
                        }
                        if (scope.desk) {
                        	scope.stages = desks.deskStages[scope.desk._id];
                        }
                    });
                };

                scope.$watch('item', function() {
                    fetchDesks()
                    .then(function() {
                        fetchStages();
                    });
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
                    scope.beforeSend()
                    .then(function(result) {
		    			scope.task._etag = result._etag;
                        api.save('tasks', scope.task, data).then(gotoDashboard);
                    });
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

        .service('authoring', AuthoringService)
        .service('autosave', AutosaveService)
        .service('confirm', ConfirmDirtyService)
        .service('lock', LockService)

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
                    resolve: {
                        item: ['$route', 'authoring', function($route, authoring) {
                            return authoring.open($route.current.params._id);
                        }]
                    }
	            })
	            .activity('edit.text', {
	            	label: gettext('Edit item'),
	            	icon: 'pencil',
	            	controller: ['data', '$location', 'workqueue', 'superdesk', function(data, $location, workqueue, superdesk) {
	            		workqueue.add(data.item);
                        superdesk.intent('author', 'article', data.item);
	                }],
	            	filters: [
	                    {action: 'list', type: 'archive'}
	                ]
	            });
        }]);
})();
