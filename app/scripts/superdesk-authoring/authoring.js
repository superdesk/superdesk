(function() {
    'use strict';

    var CONTENT_FIELDS_DEFAULTS = {
        headline: '',
        slugline: '',
        body_html: null,
        'abstract': null,
        anpa_take_key: null,
        byline: null,
        urgency: null,
        priority: null,
        subject: [],
        'anpa-category': {},
        genre: [],
        usageterms: null,
        ednote: null,
        place: [],
        located: null,
        dateline: '',
        language: null
    };

    /**
     * Extend content of dest
     *
     * @param {Object} dest
     * @param {Object} src
     */
    function extendItem(dest, src) {
        return angular.extend(dest, _.pick(src, _.keys(CONTENT_FIELDS_DEFAULTS)));
    }

    /**
     * Extend content of dest by forcing 'default' values
     * if the value doesn't exist in src
     *
     * @param {Object} dest
     * @param {Object} src
     */
    function forcedExtend(dest, src) {
        _.each(CONTENT_FIELDS_DEFAULTS, function(value, key) {
            if (dest[key]) {
                if (src[key]) {
                    dest[key] = src[key];
                } else {
                    dest[key] = value;
                }
            } else {
                if (src[key]) {
                    dest[key] = src[key];
                }
            }
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
            if (diff && diff._etag) {
                item._etag = diff._etag;
            }
            diff = extendItem({}, diff);
            return api.save('archive', item, diff).then(function(_item) {
                item._autosave = null;
                item._locked = lock.isLocked(item);
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
            item._locked = true;
            confirm.unlock(userId);
        };
    }

    LockService.$inject = ['$q', 'api', 'session', 'privileges'];
    function LockService($q, api, session, privileges) {

        /**
         * Lock an item
         */
        this.lock = function lock(item, force) {
            if (!item.lock_user || force) {
                return api.save('archive_lock', {}, {}, item).then(function(lock) {
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

        /**
        * can unlock the item or not.
        */
        this.can_unlock = function can_unlock(item) {
            if (this.isLockedByMe(item)) {
                return true;
            } else {
                return privileges.privileges.unlock;
            }
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
        'api',
        'session',
        'lock',
        'privileges',
        'ContentCtrl',
        '$location',
        'referrer'
    ];

    function AuthoringController($scope, superdesk, workqueue, notify, gettext,
                                 desks, item, authoring, api, session, lock, privileges,
                                 ContentCtrl, $location, referrer) {
        var stopWatch = angular.noop,
            _closing;

        $scope.privileges = privileges.privileges;
        $scope.content = new ContentCtrl($scope);

        $scope.workqueue = workqueue.all();
        $scope.dirty = false;
        $scope.viewSendTo = false;
        $scope.stage = null;
        $scope.widget_target = 'authoring';

        $scope.proofread = false;

        // TODO These values should come from preferences.
        $scope.limits = {
            slugline: 24,
            headline: 64,
            'abstract': 160
        };

        $scope.referrerUrl = referrer.getReferrerUrl();

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
                'item.place',
                'item.language',
                'item.type'
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
                if (angular.isDefined(response.data._issues)) {
                    if (angular.isDefined(response.data._issues.unique_name) &&
                        response.data._issues.unique_name.unique === 1) {
                        notify.error(gettext('Error: Unique Name is not unique.'));
                    } else if (angular.isDefined(response.data._issues['validator exception'])) {
                        notify.error(gettext('Error: ' + response.data._issues['validator exception']));
                    }
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
                $location.url($scope.referrerUrl);
            });
        };

        /**
         * Preview different version of an item
         */
        $scope.preview = function(version) {
            stopWatch();
            forcedExtend($scope.item, version);
            $scope._editable = false;
        };

        /**
         * Revert item to given version
         */
        $scope.revert = function(version) {
            forcedExtend($scope.item, version);
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

        /**
         * Checks if the item can be unlocked or not.
         */
        $scope.can_unlock = function() {
            return lock.can_unlock($scope.item);
        };

        $scope.unlock = function() {
            lock.unlock($scope.item).then(function(unlocked_item) {
                extendItem($scope.item, unlocked_item);
                lock.lock(unlocked_item, true).then(function(result) {
                    extendItem($scope.item, result);
                    $scope.item.lock_user = result.lock_user;
                    $scope.item._locked = result._locked;
                    $scope._editable = true;
                    startWatch();
                });
            });
        };

        // init
        $scope.closePreview();

        $scope.$on('item:unlock', function(_e, data) {
            if ($scope.item._id === data.item && !_closing) {
                stopWatch();
                authoring.unlock(item, data.user);
                $scope._editable = false;
                $scope.item._locked = true;
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
                html: '@'
            },
            template: '<span class="char-count" ng-class="{error: numChars > limit}" translate>{{numChars}}/{{ limit }} characters </span>',
            link: function characterCountLink(scope, elem, attrs) {
                scope.html = scope.html || false;
                scope.numChars = 0;
                scope.$watch('item', function() {
                    var input = scope.item || '';
                    input = scope.html ? cleanHtml(input) : input;
                    scope.numChars = input.length || 0;
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

    AuthoringThemesService.$inject = ['storage', 'preferencesService'];
    function AuthoringThemesService(storage, preferencesService) {

        var service = {};

        var PREFERENCES_KEY = 'editor:theme';
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

        service.save = function(key, theme) {
            return preferencesService.get().then(function(result) {
                result[PREFERENCES_KEY][key] = theme.key;
                return preferencesService.update(result);
            });
        };

        service.get = function(key) {
            return preferencesService.get().then(function(result) {
                var theme = result[PREFERENCES_KEY] && result[PREFERENCES_KEY][key] ? result[PREFERENCES_KEY][key] : THEME_DEFAULT;
                return _.find(service.availableThemes, {key: theme});
            });
        };

        return service;
    }

    ThemeSelectDirective.$inject = ['authThemes'];
    function ThemeSelectDirective(authThemes) {

        return {
            templateUrl: 'scripts/superdesk-authoring/views/theme-select.html',
            scope: {
                key: '@'
            },
            link: function themeSelectLink(scope, elem) {

                var DEFAULT_CLASS = 'main-article';

                scope.themes = authThemes.availableThemes;
                authThemes.get(scope.key).then(function(theme) {
                    scope.theme = theme;
                    applyTheme();
                });

                scope.changeTheme = function(theme) {
                    scope.theme = theme;
                    authThemes.save(scope.key, theme);
                    applyTheme();
                };

                function applyTheme() {
                    elem.closest('#theme-container')
                        .attr('class', DEFAULT_CLASS)
                        .addClass(scope.theme && scope.theme.cssClass);
                }
            }
        };
    }

    SendItem.$inject = ['$q', 'superdesk', 'api', 'desks', 'notify', '$location'];
    function SendItem($q, superdesk, api, desks, notify, $location) {
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
                        api.save('tasks', scope.task, data).then(gotoPreviousScreen);
                    });
                }

                function gotoPreviousScreen($scope) {
                    notify.success(gettext('Item sent.'));
                    $location.url(scope.$parent.referrerUrl);
                }
            }
        };
    }

    function ContentCreateDirective() {
        return {
            templateUrl: 'scripts/superdesk-authoring/views/sd-content-create.html'
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
            'superdesk.authoring.packages',
            'superdesk.authoring.find-replace',
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
        .directive('sdContentCreate', ContentCreateDirective)

        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('authoring', {
                    category: '/authoring',
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
                    priority: 10,
	            	icon: 'pencil',
	            	controller: ['data', '$location', 'workqueue', 'superdesk', function(data, $location, workqueue, superdesk) {
	            		workqueue.add(data.item);
                        superdesk.intent('author', 'article', data.item);
	                }],
	            	filters: [
	                    {action: 'list', type: 'archive'}
	                ],
                    condition: function(item) {
                        return item.type !== 'composite';
                    }
	            });
        }]);
})();
