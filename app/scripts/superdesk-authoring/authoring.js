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
         *   and save it if dirty, unlock if editable, and remove from work queue at all times
         *
         * @param {Object} item Destination.
         * @param {Object} diff Changes.
         * @param {boolean} isDirty $scope dirty status.
         */
        this.close = function closeAuthoring(item, diff, isDirty) {
            var promise = $q.when();

            if (this.isEditable(item)) {
                if (isDirty) {
                    promise = confirm.confirm()
                        .then(angular.bind(this, function save() {
                            return this.save(item, diff);
                        }), function() { // ignore saving
                            return $q.when();
                        });
                }

                promise = promise.then(function unlock() {
                    return lock.unlock(item);
                });
            }

            return promise.then(function removeFromWorkqueue(res) {
                return workqueue.remove(item);
            });
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
        var stopWatch = angular.noop,
            _closing;

        $scope.workqueue = workqueue.all();
        $scope.dirty = false;
        $scope.viewSendTo = false;
        $scope.stage = null;

        // These values should come from preferences.
        $scope.sluglineSoftLimit = 26;
        $scope.sluglineHardLimit = 40;
        $scope.headlineSoftLimit = 42;
        $scope.headlineHardLimit = 70;
        $scope.abstractSoftLimit = 160;
        $scope.abstractHardLimit = 200;

        $scope.charLimitHit = false;

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
                'item.abstract',
                'item.slugline',
                'item.body_html',
                'item.abstract',
                'item.anpa_take_key',
                'item.unique_name',
                'item.urgency',
                'item.byline',
                'item.priority',
                'item.ednote',
                'item.usageterms',
                'item.subject',
                'item.genre',
                'item[\'anpa-category\']',
                'item.dateline',
                'item.located',
                'item.place'
            ], function(changes) {
                $scope.dirty = isDirty();
                if ($scope.dirty && authoring.isEditable(item)) {
                    authoring.autosave(item, $scope.item);
                }
            });
        }

        $scope.checkLimit = function() {
            $scope.charLimitHit = false;
            _.each({
                'slugline': $scope.sluglineSoftLimit,
                'headline': $scope.headlineSoftLimit,
                'abstract': $scope.abstractSoftLimit
            }, function(limit, field) {
                if ($scope.item[field] && $scope.item[field].length > limit) {
                    $scope.charLimitHit = true;
                    return false;
                }
            });
        };

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
                if (angular.isDefined(response.data._issues) &&
                    angular.isDefined(response.data._issues.unique_name) &&
                    response.data._issues.unique_name.unique === 1) {
                    notify.error(gettext('Error: Unique Name is not unique.'));
                } else {
                    notify.error(gettext('Error. Item not updated.'));
                }
    		});
    	};

        /**
         * Close an item - unlock and remove from workqueue
         */
        $scope.close = function() {
            stopWatch();
            _closing = true;
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
            if ($scope.item._id === data.item && !_closing) {
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

    var cleanHtml = function(data) {
        return data.replace(/<\/?[^>]+>/gi, '').replace('&nbsp;', ' ');
    };

    CharacterCount.$inject = [];
    function CharacterCount() {
        return {
            scope: {
                item: '=',
                limit: '=',
                limitCallback: '=',
                html: '@'
            },
            template: '<span class="char-count" ng-class="{error: limitHit}">{{numChars}} <span translate>characters</span></span>',
            link: function characterCountLink(scope, elem, attrs) {
                scope.html = scope.html || false;
                scope.numChars = 0;
                scope.limitHit = false;

                scope.$watch('item', function() {
                    var input = scope.item || '';
                    input = scope.html ? cleanHtml(input) : input;

                    scope.numChars = input.length || 0;
                    if (scope.limit && (
                        (scope.numChars > scope.limit && scope.limitHit === false) ||
                        (scope.numChars <= scope.limit && scope.limitHit === true)
                    )) {
                        scope.limitHit = !scope.limitHit;
                        if (typeof scope.limitCallback === 'function') {
                            scope.limitCallback();
                        }
                    }
                });
            }
        };
    }

    WordCount.$inject = [];
    function WordCount() {
        return {
            scope: {
                item: '=',
                html: '@'
            },
            template: '<span class="char-count">{{numWords}} <span translate>words</span></span>',
            link: function wordCountLink(scope, elem, attrs) {
                scope.html = scope.html || false;
                scope.numWords = 0;

                scope.$watch('item', function() {
                    var input = scope.item || '';
                    input = scope.html ? cleanHtml(input) : input;

                    scope.numWords = _.compact(input.split(/\s+/)).length || 0;
                });
            }
        };
    }

    AuthoringThemesService.$inject = ['storage'];
    function AuthoringThemesService(storage) {

        var service = {};

        var THEME_KEY = 'authoring:theme';
        var THEME_DEFAULT = 'default-normal';

        service.availableThemes = [
            {
                cssClass: '',
                label: 'Default Theme normal',
                key: 'default-normal'
            },
            {
                cssClass: 'large-text',
                label: 'Default Theme large',
                key: 'default-large'
            },
            {
                cssClass: 'dark-theme',
                label: 'Dark Theme normal',
                key: 'dark-normal'
            },
            {
                cssClass: 'dark-theme large-text',
                label: 'Dark Theme large',
                key: 'dark-large'
            },
            {
                cssClass: 'natural-theme',
                label: 'Natural Theme normal',
                key: 'natural-normal'
            },
            {
                cssClass: 'natural-theme large-text',
                label: 'Natural Theme large',
                key: 'natural-large'
            }
        ];

        service.defaultTheme = 'default-normal';

        service.save = function(theme) {
            storage.setItem(THEME_KEY, theme.key);
        };

        service.get = function() {
            var _default = storage.getItem(THEME_KEY) || THEME_DEFAULT;
            return _.find(service.availableThemes, {key: _default});
        };

        return service;
    }

    ThemeSelectDirective.$inject = ['authThemes'];
    function ThemeSelectDirective(authThemes) {

        return {
            templateUrl: 'scripts/superdesk-authoring/views/theme-select.html',
            link: function themeSelectLink(scope, elem) {

                scope.themes = authThemes.availableThemes;
                scope.theme = authThemes.get();
                applyTheme();

                scope.changeTheme = function(theme) {
                    scope.theme = theme;
                    authThemes.save(theme);
                    applyTheme();
                };

                function applyTheme() {
                    elem.closest('#theme-container').attr('class', scope.theme.cssClass);
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
        .service('authThemes', AuthoringThemesService)

        .directive('sdDashboardCard', DashboardCard)
        .directive('sdSendItem', SendItem)
        .directive('sdCharacterCount', CharacterCount)
        .directive('sdWordCount', WordCount)
        .directive('sdThemeSelect', ThemeSelectDirective)

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
