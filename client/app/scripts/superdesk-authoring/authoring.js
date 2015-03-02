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
        language: null,
        unique_name: ''
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
            timeouts = {};

        /**
         * Open an item
         */
        this.open = function openAutosave(item) {
            if (item._locked || item.read_only) {
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
        this.save = function saveAutosave(item) {
            this.stop(item);
            timeouts[item._id] = $timeout(function() {
                var diff = extendItem({_id: item._id}, item);
                return api.save(RESOURCE, {}, diff).then(function(_autosave) {
                    var orig = Object.getPrototypeOf(item);
                    orig._autosave = _autosave;
                    extendItem(orig._autosave, item);
                    extendItem(orig, item);
                });
            }, AUTOSAVE_TIMEOUT);
            return timeouts[item._id];
        };

        /**
         * Stop pending autosave
         */
        this.stop = function stopAutosave(item) {
            if (timeouts[item._id]) {
                $timeout.cancel(timeouts[item._id]);
                timeouts[item._id] = null;
            }
        };

        /**
         * Drop autosave
         */
        this.drop = function dropAutosave(item) {
            this.stop(item);
            api(RESOURCE).remove(item._autosave);
            item._autosave = null;
        };
    }

    AuthoringService.$inject = ['$q', 'api', 'lock', 'autosave', 'confirm'];
    function AuthoringService($q, api, lock, autosave, confirm) {

        /**
         * Open an item for editing
         *
         * @param {string} _id Item _id.
         */
        this.open = function openAuthoring(_id, read_only) {
            return api.find('archive', _id, {embedded: {lock_user: 1}}).then(function _lock(item) {
                item._editable = !read_only;
                return lock.lock(item);
            }).then(function _autosave(item) {
                return autosave.open(item);
            });
        };

        /**
         * Close an item
         *
         *   and save it if dirty, unlock if editable, and remove from work queue at all times
         *
         * @param {Object} diff Edits.
         * @param {boolean} isDirty $scope dirty status.
         */
        this.close = function closeAuthoring(diff, isDirty) {
            var promise = $q.when();
            if (this.isEditable(diff)) {
                if (isDirty) {
                    promise = confirm.confirm()
                        .then(angular.bind(this, function save() {
                            return this.save(diff);
                        }), function() { // ignore saving
                            return $q.when();
                        });
                }

                promise = promise.then(function unlock() {
                    return lock.unlock(diff);
                });
            }

            return promise;
        };

        /**
         * Publish an item
         *
         *   and save it if dirty
         *
         * @param {Object} diff Edits.
         * @param {boolean} isDirty $scope dirty status.
         */
        this.publish = function publishAuthoring(diff, isDirty) {
            var promise = $q.when();
            if (this.isEditable(diff)) {
                if (isDirty) {
                    promise = confirm.confirmPublish()
                        .then(angular.bind(this, function save() {
                            return this.save(diff);
                        }), function() { // cancel
                            return false;
                        });
                }
            }

            return promise;
        };
        /**
         * Autosave the changes
         *
         * @param {Object} item
         */
        this.autosave = function autosaveAuthoring(item) {
            return autosave.save(item);
        };

        /**
         * Save the item
         *
         * @param {Object} item
         */
        this.save = function saveAuthoring(item) {
            var diff = extendItem({}, item);
            autosave.stop(item);
            return api.save('archive', item, diff).then(function(_item) {
                item._autosave = null;
                item._locked = lock.isLocked(item);
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
            autosave.stop(item);
            item.lock_session = null;
            item.lock_user = null;
            item._locked = false;
            confirm.unlock(userId);
        };

        /**
         * Lock an item - callback for item:lock event
         *
         * @param {Object} item
         * @param {string} userId
         */
        this.lock = function lock(item, userId) {
            autosave.stop(item);
            api.find('users', userId).then(function(user) {
                item.lock_user = user;
            }, function(rejection) {
                item.lock_user = userId;
            });
            item._locked = true;
        };
    }

    LockService.$inject = ['$q', 'api', 'session', 'privileges'];
    function LockService($q, api, session, privileges) {

        /**
         * Lock an item
         */
        this.lock = function lock(item, force) {
            if ((!item.lock_user && item._editable) || force) {
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
            var userId = getLockedUserId(item);

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

        function getLockedUserId(item) {
            return item.lock_user && item.lock_user._id || item.lock_user;
        }

        /**
        * Test is an item is locked by me in another session
        */
        this.isLockedByMe = function isLockedByMe(item) {
            var userId = getLockedUserId(item);
            return userId && userId === session.identity._id && item.lock_session !== session.sessionId;
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
         * In case $scope is dirty ask user if he want's to save changes and publish.
         */
        this.confirmPublish = function confirmPublish() {
            return modal.confirm(
                gettext('There are some unsaved changes, do you want to save it and publish now?'),
                gettext('Save changes?'),
                gettext('Save and publish'),
                gettext('Cancel')
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

        /**
         * Make user aware that an item was locked
         *
         * @param {string} userId Id of user who locked an item.
         */
        this.lock = function lock(userId) {
            api.find('users', userId).then(function(user) {
                var msg = gettext('This item was locked by <b>{{ user }}</b>.').
                    replace('{{ user }}', $filter('username')(user));
                return modal.confirm(msg, gettext('Item locked'), gettext('OK'), false);
            });
        };
    }

    AuthoringController.$inject = [
        '$scope',
        'superdesk',
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
        'referrer',
        '$timeout'
    ];

    function AuthoringController($scope, superdesk, notify, gettext,
                                 desks, item, authoring, api, session, lock, privileges,
                                 ContentCtrl, $location, referrer, $timeout) {
        var _closing;

        $scope.privileges = privileges.privileges;
        $scope.content = new ContentCtrl($scope);

        $scope.dirty = false;
        $scope.viewSendTo = false;
        $scope.stage = null;
        $scope._editable = item._editable;
        $scope.widget_target = 'authoring';

        $scope.sending = false;

        $scope.proofread = false;

        $scope.referrerUrl = referrer.getReferrerUrl();

        if (item.task && item.task.stage) {
            api('stages').getById(item.task.stage)
            .then(function(result) {
                $scope.stage = result;
            });
        }

        /**
         * Create a new version
         */
    	$scope.save = function() {
    		return authoring.save($scope.item).then(function(res) {
                item = res;
                $scope.dirty = false;
                $scope.item = _.create(item);
                notify.success(gettext('Item updated.'));
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
         * Close an item - unlock
         */
        $scope.close = function() {
            _closing = true;
            authoring.close(item, $scope.dirty).then(function() {
                $location.url($scope.referrerUrl);
            });
        };

        function publishItem() {
            return api.update('archive_publish', item, {state: 'published'}).then(function(result) {
                    notify.success(gettext('Item updated.'));
                    $scope.item = result;
                    $scope.dirty = false;
                }, function(response) {
                    notify.error(gettext('Error. Item not updated.'));
                });
        }
        $scope.publish = function() {
            if ($scope.dirty) { // save & publish dialog
                authoring.publish(item, $scope.dirty)
                .then(function(res) {
                    if (res) {
                        publishItem();
                    }
                }, function(response) {
                    notify.error(gettext('Error. Item not updated.'));
                });
            } else {
                publishItem();
            }
        };

        $scope.beforeSend = function() {
            $scope.sending = true;
            return $scope.save()
            .then(function() {
                var p = lock.unlock(item);
                return p;
            });
        };

        /**
         * Preview different version of an item
         */
        $scope.preview = function(version) {
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
        };

        /**
         * Checks if the item can be unlocked or not.
         */
        $scope.can_unlock = function() {
            return lock.can_unlock($scope.item);
        };
        $scope.save_enabled = function() {
            return $scope.dirty || $scope.item._autosave;
        };

        function updateEditorState (result) {
            extendItem($scope.item, result);

            //The current $digest cycle will mark $scope.dirty = true.
            //We need to postpone this code block for the next cycle.
            $timeout(function() {
                item.lock_user = $scope.item.lock_user = result.lock_user;
                $scope.item._locked = result._locked;
                item.lock_session = $scope.item.lock_session = result.lock_session;
                $scope._editable = $scope.item._editable = true;
                $scope.dirty = false;
                $scope.item._autosave = null;
            }, 200);
        }

        $scope.unlock = function() {
            lock.unlock($scope.item).then(function(unlocked_item) {
                lock.lock(unlocked_item, true).then(updateEditorState);
            });
        };

        $scope.lock = function() {
            var path = $location.path();
            if (path.indexOf('/view') < 0) {
               lock.lock($scope.item, true).then(updateEditorState);
            } else {
                superdesk.intent('author', 'article', item);
            }
        };

        $scope.isLockedByMe = function() {
            return lock.isLockedByMe($scope.item);
        };

        $scope.autosave = function(item) {
            $scope.dirty = true;
            return authoring.autosave(item);
        };

        // init
        $scope.closePreview();

        $scope.$on('item:lock', function(_e, data) {
            if ($scope.item._id === data.item && !_closing &&
                session.sessionId !== data.lock_session) {
                var path = $location.path();
                if (path.indexOf('/view') < 0) {
                   authoring.lock($scope.item, data.user);
                   $location.url($scope.referrerUrl);
                }
            }
        });

        $scope.$on('item:unlock', function(_e, data) {
            if ($scope.item._id === data.item && !_closing &&
                session.sessionId !== data.lock_session) {
                authoring.unlock($scope.item, data.user);
                $scope._editable = $scope.item._editable = false;
                $scope.item._locked = false;
                $scope.item.lock_session = null;
                $scope.item.lock_user = null;
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
            scope: {key: '@'},
            link: function themeSelectLink(scope, elem) {

                var DEFAULT_CLASS = 'main-article theme-container';

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
                    elem.closest('.theme-container')
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

    function HighlightCreateDirective() {
        return {
            templateUrl: 'scripts/superdesk-authoring/views/sd-highlight-create.html'
        };
    }

    ArticleEditDirective.$inject = ['autosave'];
    function ArticleEditDirective(autosave) {
        // TODO(petr): These values should come from preferences.
        var limits = {
            slugline: 24,
            headline: 64,
            'abstract': 160
        };

        return {
            templateUrl: 'scripts/superdesk-authoring/views/article-edit.html',
            link: function(scope) {
                scope.limits = limits;

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
        .directive('sdHighlightCreate', HighlightCreateDirective)
        .directive('sdArticleEdit', ArticleEditDirective)

        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('authoring', {
                    category: '/authoring',
                    href: '/authoring/:_id',
                    when: '/authoring/:_id',
                	label: gettext('Authoring'),
	                templateUrl: 'scripts/superdesk-authoring/views/authoring.html',
                    topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
	                controller: AuthoringController,
	                filters: [{action: 'author', type: 'article'}],
                    resolve: {
                        item: ['$route', 'authoring', function($route, authoring) {
                            return authoring.open($route.current.params._id, false);
                        }]
                    }
	            })
                .activity('edit.text', {
	            	label: gettext('Edit item'),
                    href: '/authoring/:_id',
                    priority: 10,
	            	icon: 'pencil',
                    controller: ['data', 'superdesk', function(data, superdesk) {
                        superdesk.intent('author', 'article', data.item);
	                }],
                    filters: [{action: 'list', type: 'archive'}],
                    condition: function(item) { //console.log(item);
                        return item.type !== 'composite' && item.state !== 'published';
                    }
	            })
	            .activity('view.text', {
	            	label: gettext('View item'),
                    priority: 2000,
	            	icon: 'fullscreen',
	            	controller: ['data', 'superdesk', function(data, superdesk) {
                        superdesk.intent('read_only', 'content_article', data.item);
	                }],
                    filters: [{action: 'list', type: 'archive'}],
                    condition: function(item) {
                        return item.type !== 'composite';
                    }
	            })
                .activity('read_only.content_article', {
                    category: '/authoring',
                    href: '/authoring/:_id/view',
                    when: '/authoring/:_id/view',
                	label: gettext('Authoring Read Only'),
	                templateUrl: 'scripts/superdesk-authoring/views/authoring.html',
                    topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
	                controller: AuthoringController,
	                filters: [{action: 'read_only', type: 'content_article'}],
                    resolve: {
                        item: ['$route', 'authoring', function($route, authoring) {
                            return authoring.open($route.current.params._id, true);
                        }]
                    }
	            });
        }]);
})();
