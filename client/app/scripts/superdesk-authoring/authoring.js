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
        groups: [],
        usageterms: null,
        ednote: null,
        place: [],
        located: null,
        dateline: '',
        language: null,
        unique_name: '',
        keywords: [],
        description: null,
        destination_groups: null,
        sign_off: null
    };

    var KILL_TEMPLATE = {
        headline: 'Kill/Takedown notice ~~~ Kill/Takedown notice',
        'abstract': 'This article has been removed',
        anpa_take_key: 'KILL/TAKEDOWN',
        body: ['Please kill story slugged ${ keyword } ex ${ dateline } at ${ date_published }.',
               'Pursuant to your Information Supply Agreement with Australian Associated Press (AAP), AAP requests that',
               'you remove the above story from any media you publish and access to the story be immediately disabled ',
               'including but not limited to those websites in either your direct or indirect possession, custody, or control.',
               'AAP has become aware that the story may potentially expose AAP and those who publish the story to the risk of:',
               '[insert relevant option/s from below]',
               ' - a claim in defamation.',
               '- a possible prosecution for contempt.',
               '- a contempt prosecution arising out of breach of an order of the Family/Supreme/District/Federal Court.',
               '- a breach of a law prohibiting publication.',
               '- a breach of a law prohibiting publication that applies retrospectively.',
               '- a breach of any State or Commonwealth privacy laws.',
               '- a claim for damages.',
               '- publishing extremely erroneous material.',
               'This kill/takedown is mandatory, and no further use can be made of the story. ',
               'A replacement story will be issued shortly/will not be issued.',
               'AAP will not be liable for any losses, costs and expenses, damages and other costs (including without limitation',
               ' reasonable legal costs), indirect, consequential special or punitive loss or damage, arising out of the story and ',
               'this Notice suffered or incurred by you after receipt of this Notice.'
               ]
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
                    extendItem(item, _autosave);
                    var orig = Object.getPrototypeOf(item);
                    orig._autosave = _autosave;
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

        this.limits = {
            slugline: 24,
            headline: 64,
            'abstract': 160
        };

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
         * @param {Object} diff
         * @param {Object} orig
         * @param {boolean} isDirty $scope dirty status.
         */
        this.close = function closeAuthoring(diff, orig, isDirty) {
            var promise = $q.when();
            if (this.isEditable(diff)) {
                if (isDirty) {
                    promise = confirm.confirm()
                        .then(angular.bind(this, function save() {
                            return this.save(orig, diff);
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
         * @param {Object} orig original item.
         * @param {Object} diff Edits.
         * @param {boolean} isDirty $scope dirty status.
         */
        this.publishConfirmation = function publishAuthoring(orig, diff, isDirty) {
            var promise = $q.when();
            if (this.isEditable(diff) && isDirty) {
                promise = confirm.confirmPublish()
                    .then(angular.bind(this, function save() {
                        return true;
                    }), function() { // cancel
                        return false;
                    });
            }

            return promise;
        };

        this.publish = function publish(orig, diff, action) {
            action = action || 'publish';
            diff = extendItem({}, diff);
            var endpoint = 'archive_' + action;
            return api.update(endpoint, orig, diff)
            .then(function(result) {
                return lock.unlock(result)
                    .then(function(result) {
                        return result;
                    });
            }, function(response) {
                return response;
            });
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
         * @param {Object} origItem
         * @param {Object} item
         */
        this.save = function saveAuthoring(origItem, item) {
            var diff = extendItem({}, item);

            // Finding if all the keys are dirty for real
            if (angular.isDefined(origItem)) {
                angular.forEach(_.keys(diff), function(key) {
                    if (_.isEqual(diff[key], origItem[key])) {
                        delete diff[key];
                    }
                });
            }

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

    LockService.$inject = ['$q', 'api', 'session', 'privileges', 'notify'];
    function LockService($q, api, session, privileges, notify) {
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
                    notify.error(gettext('Failed to get a lock on the item!'));
                    item._locked = true;
                    item._editable = false;
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
        * Test if an item is locked by me in another session
        */
        this.isLockedByMe = function isLockedByMe(item) {
            var userId = getLockedUserId(item);
            return userId && userId === session.identity._id;
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
                gettext('Ignore'),
                gettext('Cancel')
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

    AuthoringController.$inject = ['$scope', 'item', 'action'];
    function AuthoringController($scope, item, action) {
        $scope.origItem = item;
        $scope.action = action || 'edit';

        $scope.widget_target = 'authoring';

        $scope.intentFilter = {
            action: 'author',
            type: 'article'
        };
    }

    AuthoringDirective.$inject = [
        'superdesk',
        'notify',
        'gettext',
        'adminPublishSettingsService',
        'desks',
        'authoring',
        'api',
        'session',
        'lock',
        'privileges',
        'ContentCtrl',
        '$location',
        'referrer',
        'macros',
        '$timeout',
        '$q'
    ];
    function AuthoringDirective(superdesk, notify, gettext, adminPublishSettingsService,
                                desks, authoring, api, session, lock, privileges,
                                ContentCtrl, $location, referrer, macros, $timeout, $q) {
        return {
            link: function($scope) {
                var _closing;

                $scope.privileges = privileges.privileges;
                $scope.content = new ContentCtrl($scope);

                $scope.dirty = false;
                $scope.views = {send: false};
                $scope.stage = null;
                $scope._editable = $scope.origItem._editable;
                $scope.isMediaType = _.contains(['audio', 'video', 'picture'], $scope.origItem.type);
                $scope.action = $scope.action || ($scope.editable ? 'edit' : 'view');
                $scope.publish_enabled = $scope.origItem && $scope.origItem.task && $scope.origItem.task.desk &&
                    ((!_.contains(['published', 'killed'], $scope.origItem.state) && $scope.privileges.publish === 1) ||
                     ($scope.origItem.state === 'published' && $scope.privileges.kill === 1));
                $scope.save_visible = $scope._editable && !_.contains(['published', 'killed'], $scope.origItem.state);

                if ($scope.action === 'kill') {
                    $scope.origItem.headline = KILL_TEMPLATE.headline;
                    $scope.origItem['abstract'] = KILL_TEMPLATE['abstract'];
                    $scope.origItem.anpa_take_key = KILL_TEMPLATE.anpa_take_key;
                    var template = _.template(KILL_TEMPLATE.body.join('<br/>'));
                    $scope.origItem.body_html = template({'keyword': $scope.origItem.slugline,
                                                          'dateline': $scope.origItem.dateline,
                                                          'date_published': $scope.origItem.versioncreated});
                }

                $scope.origItem.sign_off = $scope.origItem.sign_off || $scope.origItem.version_creator;
                $scope.origItem.destination_groups = $scope.origItem.destination_groups || [];

                if ($scope.origItem.destination_groups && $scope.origItem.destination_groups.length) {
                    adminPublishSettingsService.fetchDestinationGroupsByIds($scope.origItem.destination_groups)
                        .then(function(result) {
                            var destinationGroups = [];
                            _.each(result._items, function(item) {
                                destinationGroups.push(item);
                            });
                            $scope.vars = {destinationGroups: destinationGroups};
                        });
                } else {
                    $scope.vars = {destinationGroups: []};
                }

                $scope.$watch('vars', function() {
                    if ($scope.vars && $scope.vars.destinationGroups) {
                        var destinationGroups = _.pluck($scope.vars.destinationGroups, '_id').sort();
                        if (!_.isEqual(destinationGroups, $scope.item.destination_groups)) {
                            $scope.item.destination_groups = destinationGroups;
                            $scope.autosave($scope.item);
                        }
                    }
                }, true);

                $scope.proofread = false;
                $scope.referrerUrl = referrer.getReferrerUrl();

                if ($scope.origItem.task && $scope.origItem.task.stage) {
                    api('stages').getById($scope.origItem.task.stage)
                    .then(function(result) {
                        $scope.stage = result;
                    });
                }

                /**
                 * Create a new version
                 */
                $scope.save = function() {
                    return authoring.save($scope.origItem, $scope.item).then(function(res) {
                        $scope.origItem = res;
                        $scope.dirty = false;
                        $scope.item = _.create($scope.origItem);
                        notify.success(gettext('Item updated.'));
                        return $scope.origItem;
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

                function validateDestinationGroups(item) {
                    if (!item.destination_groups || !item.destination_groups.length) {
                        return $q.reject();
                    }
                    return adminPublishSettingsService.fetchDestinationGroupsByIds(item.destination_groups)
                    .then(function(result) {
                        if (result._items.length !== item.destination_groups.length) {
                            return $q.reject();
                        }
                        return true;
                    });
                }

                function publishItem(orig, item) {
                    var action = $scope.action === 'kill' ? 'kill' : 'publish';
                    authoring.publish(orig, item, action)
                    .then(function(response) {
                        if (response) {
                            if (angular.isDefined(response.data) && angular.isDefined(response.data._issues)) {
                                if (angular.isDefined(response.data._issues['validator exception'])) {
                                    notify.error(gettext('Error: ' + response.data._issues['validator exception']));
                                }
                            } else {
                                notify.success(gettext('Item published.'));
                                $scope.item = response;
                                $scope.dirty = false;
                                $location.url($scope.referrerUrl);
                            }
                        } else {
                            notify.error(gettext('Unknown Error: Item not published.'));
                        }
                    });
                }

                $scope.publish = function() {
                    validateDestinationGroups($scope.item)
                    .then(function() {
                        if ($scope.dirty) { // save dialog & then publish if confirm
                            authoring.publishConfirmation($scope.origItem, $scope.item, $scope.dirty)
                            .then(function(res) {
                                if (res) {
                                    publishItem($scope.origItem, $scope.item);
                                }
                            }, function(response) {
                                notify.error(gettext('Error. Item not published.'));
                            });
                        } else { // Publish
                            publishItem($scope.origItem, $scope.item);
                        }
                    }, function(res) {
                        notify.error(gettext('Error. Destination groups invalid.'));
                    });
                };

                /**
                 * Close an item - unlock
                 */
                $scope.close = function() {
                    _closing = true;
                    authoring.close($scope.item, $scope.origItem, $scope.dirty).then(function() {
                        $location.url($scope.referrerUrl);
                    });
                };

                $scope.beforeSend = function() {
                    $scope.sending = true;
                    return $scope.save()
                    .then(function() {
                        var p = lock.unlock($scope.origItem);
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
                    $scope.item = _.create($scope.origItem);
                    extendItem($scope.item, $scope.item._autosave || {});
                    $scope._editable = authoring.isEditable($scope.origItem);
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
                        $scope.origItem.lock_user = $scope.item.lock_user = result.lock_user;
                        $scope.item._locked = result._locked;
                        $scope.origItem.lock_session = $scope.item.lock_session = result.lock_session;
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
                        superdesk.intent($scope.intentFilter.action, $scope.intentFilter.type, $scope.origItem);
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

                $scope.openStage = function openStage() {
                    desks.setWorkspace($scope.item.task.desk, $scope.item.task.stage);
                    superdesk.intent('view', 'content');
                };

                macros.setupShortcuts($scope);
            }
        };
    }

    function AuthoringTopbarDirective() {
        return {templateUrl: 'scripts/superdesk-authoring/views/authoring-topbar.html'};
    }

    function AuthoringSidebarDirective() {
        return {templateUrl: 'scripts/superdesk-authoring/views/authoring-sidebar.html'};
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
    SendItem.$inject = ['$q', 'superdesk', 'api', 'desks', 'notify', '$location', 'macros', '$rootScope'];
    function SendItem($q, superdesk, api, desks, notify, $location, macros, $rootScope) {
        return {
            scope: {
                item: '=',
                view: '=',
                _beforeSend: '=beforeSend',
                mode: '@'
            },
            templateUrl: 'scripts/superdesk-authoring/views/send-item.html',
            link: function sendItemLink(scope, elem, attrs) {
                scope.mode = scope.mode || 'authoring';

                scope.desks = null;
                scope.stages = null;
                scope.macros = null;

                scope.selectedDesk = null;
                scope.selectedStage = null;
                scope.selectedMacro = null;

                scope.task = null;

                scope.beforeSend = scope._beforeSend || $q.when;
                scope.macros = null;

                scope.selectedDesk = null;
                scope.selectedStage = null;
                scope.selectedMacro = null;

                scope.task = null;

                scope.beforeSend = scope._beforeSend || $q.when;

                scope.$watch('item', function() {
                    if (scope.item) {
                        desks.initialize()
                        .then(fetchDesks)
                        .then(fetchStages)
                        .then(fetchMacros);
                    }
                });

                scope.close = function() {
                    if (scope.$parent.views) {
                        scope.$parent.views.send = false;
                    } else {
                        scope.item = null;
                    }
                    $location.search('fetch', null);
                };

                scope.selectDesk = function(desk) {
                    scope.selectedDesk = _.cloneDeep(desk);
                    scope.selectedStage = null;
                    fetchStages();
                    fetchMacros();
                };

                scope.selectStage = function(stage) {
                    scope.selectedStage = stage;
                };
                scope.selectMacro = function(macro) {
                    if (scope.selectedMacro === macro) {
                        scope.selectedMacro = null;
                    } else {
                        scope.selectedMacro = macro;
                    }
                };
                scope.send = function(open) {
                    var deskId = scope.selectedDesk._id;
                    var stageId = scope.selectedStage._id || scope.selectedDesk.incoming_stage;
                    if (scope.mode === 'authoring') {
                        return sendAuthoring(deskId, stageId, scope.selectedMacro);
                    } else if (scope.mode === 'archive') {
                        return sendContent(deskId, stageId, scope.selectedMacro, open);
                    } else if (scope.mode === 'ingest') {
                        return sendIngest(deskId, stageId, scope.selectedMacro, open);
                    }
                };

                var runMacro = function(item, macro) {
                    var p;
                    if (macro) {
                        p = macros.call(macro, item)
                        .then(function(result) {
                            return api.save('archive', item, extendItem({}, result));
                        });
                    } else {
                        p = $q.when(item);
                    }
                    return p;
                };

                var sendAuthoring = function(deskId, stageId, macro) {
                    runMacro(scope.item, macro)
                    .then(function(item) {
                        api.find('tasks', scope.item._id)
                        .then(function(task) {
                            scope.task = task;
                            return scope.beforeSend();
                        })
                        .then(function(result) {
                            if (result && result._etag) {
                                scope.task._etag = result._etag;
                            }
                            return api.save('tasks', scope.task, {
                                task: _.extend(scope.task.task, {desk: deskId, stage: stageId})
                            });
                        })
                        .then(function() {
                            notify.success(gettext('Item sent.'));
                            $location.url(scope.$parent.referrerUrl);
                        });
                    });
                };

                var sendContent = function(deskId, stageId, macro, open) {
                    var finalItem;
                    api.save('duplicate', {}, {desk: scope.item.task.desk}, scope.item)
                    .then(function(item) {
                        return api.find('archive', item._id);
                    })
                    .then(function(item) {
                        return runMacro(item, macro);
                    })
                    .then(function(item) {
                        finalItem = item;
                        return api.find('tasks', item._id);
                    })
                    .then(function(_task) {
                        scope.task = _task;
                        api.save('tasks', scope.task, {
                            task: _.extend(scope.task.task, {desk: deskId, stage: stageId})
                        });
                    })
                    .then(function() {
                        notify.success(gettext('Item sent.'));
                        if (open) {
                            $location.url('/authoring/' + finalItem._id);
                        } else {
                            $rootScope.$broadcast('item:fetch');
                        }
                    });
                };

                var sendIngest = function(deskId, stageId, macro, open) {
                    var finalItem;
                    api.save('fetch', {}, {desk: deskId}, scope.item)
                    .then(function(item) {
                        return runMacro(item, macro);
                    })
                    .then(function(item) {
                        finalItem = item;
                        return api.find('tasks', item._id);
                    })
                    .then(function(_task) {
                        scope.task = _task;
                        api.save('tasks', scope.task, {
                            task: _.extend(scope.task.task, {desk: deskId, stage: stageId})
                        });
                    })
                    .then(function() {
                        notify.success(gettext('Item fetched.'));
                        if (open) {
                            $location.url('/authoring/' + finalItem._id);
                        } else {
                            $rootScope.$broadcast('item:fetch');
                        }
                    });
                };

                function fetchDesks() {
                    var p = desks.initialize()
                    .then(function() {
                        scope.desks = desks.desks;
                    });
                    if (scope.mode === 'ingest') {
                        p = p.then(function() {
                            scope.selectDesk(desks.getCurrentDesk());
                        });
                    } else {
                        p = p.then(function() {
                            var itemDesk = desks.getItemDesk(scope.item);
                            if (itemDesk) {
                                scope.selectDesk(itemDesk);
                            } else {
                                scope.selectDesk(desks.getCurrentDesk());
                            }
                        });
                    }

                    return p;

                }

                function fetchStages() {
                    if (scope.selectedDesk) {
                        scope.stages = desks.deskStages[scope.selectedDesk._id];
                        scope.selectedStage = _.find(scope.stages, {_id: scope.selectedDesk.incoming_stage});
                    }
                }

                function fetchMacros() {
                    if (scope.selectedDesk != null) {
                        macros.getByDesk(scope.selectedDesk.name)
                        .then(function(_macros) {
                            scope.macros = _macros;
                        });
                    }
                }
            }
        };
    }

    function ContentCreateDirective() {
        return {
            templateUrl: 'scripts/superdesk-authoring/views/sd-content-create.html'
        };
    }

    ArticleEditDirective.$inject = ['autosave', 'authoring'];
    function ArticleEditDirective(autosave, authoring) {
        return {
            templateUrl: 'scripts/superdesk-authoring/views/article-edit.html',
            link: function(scope) {
                scope.limits = authoring.limits;
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
            'superdesk.authoring.macros',
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
        .directive('sdArticleEdit', ArticleEditDirective)
        .directive('sdAuthoring', AuthoringDirective)
        .directive('sdAuthoringTopbar', AuthoringTopbarDirective)
        .directive('sdAuthoringSidebar', AuthoringSidebarDirective)

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
                        }],
                        action: [function() {return 'edit';}]
                    },
                    authoring: true
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
                    condition: function(item) {
                        return item.type !== 'composite' && item.state !== 'published' && item.state !== 'killed';
                    }
                })
                .activity('kill.text', {
                    label: gettext('Kill item'),
                    priority: 100,
                    icon: 'remove',
                    controller: ['data', 'superdesk', function(data, superdesk) {
                        superdesk.intent('kill', 'content_article', data.item);
                    }],
                    filters: [{action: 'list', type: 'archive'}],
                    condition: function(item) {
                        return item.type !== 'composite' && item.state === 'published';
                    },
                    privileges: {kill: 1}
                })
                .activity('kill.content_article', {
                    category: '/authoring',
                    href: '/authoring/:_id/kill',
                    when: '/authoring/:_id/kill',
                    label: gettext('Authoring Kill'),
                    templateUrl: 'scripts/superdesk-authoring/views/authoring.html',
                    topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
                    controller: AuthoringController,
                    filters: [{action: 'kill', type: 'content_article'}],
                    resolve: {
                        item: ['$route', 'authoring', function($route, authoring) {
                            return authoring.open($route.current.params._id, false);
                        }],
                        action: [function() {return 'kill';}]
                    },
                    authoring: true
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
                        }],
                        action: [function() {return 'view';}]
                    },
                    authoring: true
                });
        }])
        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('move', {
                type: 'http',
                backend: {
                    rel: 'move'
                }
            });
        }]);
})();
