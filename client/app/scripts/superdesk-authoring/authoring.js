(function() {
    'use strict';

    var CONTENT_FIELDS_DEFAULTS = Object.freeze({
        headline: '',
        slugline: '',
        body_html: null,
        'abstract': null,
        anpa_take_key: null,
        byline: null,
        urgency: null,
        priority: null,
        subject: [],
        'anpa_category': [],
        genre: [],
        groups: [],
        usageterms: null,
        ednote: null,
        place: [],
        located: null,
        dateline: null,
        language: null,
        unique_name: '',
        keywords: [],
        description: null,
        sign_off: null,
        publish_schedule: null,
        marked_for_not_publication: false,
        pubstatus: null,
        more_coming: false,
        targeted_for: [],
        embargo: null,
        renditions: null
    });

    var DEFAULT_ACTIONS = Object.freeze({
        publish: false,
        correct: false,
        kill: false,
        deschedule: false,
        new_take: false,
        re_write: false,
        save: false,
        edit: false,
        mark_item: false,
        duplicate: false,
        copy: false,
        view: true,
        spike: false,
        unspike: false,
        package_item: false,
        multi_edit: false,
        send: false
    });

    /**
     * Extend content of dest
     *
     * @param {Object} dest
     * @param {Object} src
     */
    function extendItem(dest, src) {
        return angular.extend(dest, _.pick(src, _.keys(CONTENT_FIELDS_DEFAULTS)));
    }

    function stripHtml(item) {
        var fields = ['headline', 'abstract'];
        _.each(fields, function(key) {
            if (angular.isDefined(item[key])) {
                var elem = document.createElement('div');
                elem.innerHTML = item[key];
                if (elem.textContent !== '') {
                    item[key] = elem.textContent;
                }
            }
        });
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
            if (item._locked || !item._editable) {
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
            if (item._editable && !item._locked) {
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
            }
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

            if (angular.isDefined(item._autosave) && item._autosave !== null) {
                api(RESOURCE).remove(item._autosave);
            }

            item._autosave = null;
        };
    }

    AuthoringService.$inject = ['$q', 'api', 'lock', 'autosave', 'confirm', 'privileges', 'desks'];
    function AuthoringService($q, api, lock, autosave, confirm, privileges, desks) {
        var self = this;

        this.limits = {
            slugline: 24,
            headline: 64,
            'abstract': 160
        };

        //TODO: have to trap desk update event for refereshing users desks.
        this.userDesks = [];

        desks.fetchCurrentUserDesks()
            .then(function(desks_list) {
                self.userDesks = desks_list._items;
            });

        /**
         * Open an item for editing
         *
         * @param {string} _id Item _id.
         * @param {boolean} read_only
         * @param {string} repo - repository where an item whose identifier is _id can be found.
         */
        this.open = function openAuthoring(_id, read_only, repo) {
            if (repo === 'legal_archive') {
                return api.find('legal_archive', _id).then(function(item) {
                    item._editable = false;
                    return item;
                });
            } else {
                return api.find('archive', _id, {embedded: {lock_user: 1}})
                .then(function _lock(item) {
                    item._editable = !read_only;
                    return lock.lock(item);
                }).then(function _autosave(item) {
                    return autosave.open(item);
                });
            }
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
        this.close = function closeAuthoring(diff, orig, isDirty, closeItem) {
            var promise = $q.when();
            if (this.isEditable(diff)) {
                if (isDirty) {
                    if (!_.contains(['published', 'corrected'], orig.state)) {
                        promise = confirm.confirm()
                            .then(angular.bind(this, function save() {
                                return this.save(orig, diff);
                            }), function() { // ignore saving
                                return $q.when('ignore');
                            });
                    } else {
                        promise = $q.when('ignore');
                    }
                }

                promise = promise.then(function unlock(cancelType) {
                    if (cancelType && cancelType === 'ignore') {
                        autosave.drop(orig);
                    }

                    if (!closeItem){
                        return lock.unlock(diff);
                    }
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
        this.publishConfirmation = function publishAuthoring(orig, diff, isDirty, action) {
            var promise = $q.when();
            if (this.isEditable(diff) && isDirty) {
                promise = confirm.confirmPublish(action)
                    .then(angular.bind(this, function save() {
                        return true;
                    }), function() { // cancel
                        return false;
                    });
            }

            return promise;
        };

        /**
         * Removes certain properties which are irrelevant for publish actions depending on the orig.item.state.
         * If not removed the API will throw errors.
         */
        this.cleanUpdatesBeforePublishing = function (original, updates) {
            if (!updates.publish_schedule) {
                delete updates.publish_schedule;
            }

            if (this.isPublished(original)) {
                delete updates.dateline;

                if (updates.embargo) {
                    delete updates.embargo;
                }
            }

            //check if rendition is dirty for real
            if (_.isEqual(original.renditions, updates.renditions)) {
                delete updates.renditions;
            }

            stripHtml(updates);
        };

        this.publish = function publish(orig, diff, action) {
            action = action || 'publish';
            diff = extendItem({}, diff);

            this.cleanUpdatesBeforePublishing(orig, diff);

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

        this.saveWorkConfirmation = function saveWorkAuthoring(orig, diff, isDirty, message) {
            var promise = $q.when();
            if (isDirty) {
                if (this.isEditable(diff)) {
                    promise = confirm.confirmSaveWork(message)
                        .then(angular.bind(this, function save() {
                            return this.saveWork(orig, diff);
                        }), function(err) { // cancel
                            return $q.when();
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

            stripHtml(diff);
            autosave.stop(item);

            if (_.size(diff) > 0) {
                return api.save('archive', item, diff).then(function(_item) {
                    item._autosave = null;
                    item._locked = lock.isLocked(item);
                    return item;
                });
            } else {
                return $q.when(origItem);
            }
        };

        /**
         * Save the item as new item in workspace when any critical configuration changes occur
         *
         * @param {Object} orig
         * @param {Object} item
         */
        this.saveWork = function saveWork(orig, item) {
            var _orig = {type: orig.type, version: 1, task: {desk: null, stage: null, user: orig.task.user}};
            var _diff = _.omit(item, ['unique_name', 'unique_id', '_id', 'guid']);
            var diff = extendItem(_orig, _diff);
            return api.save('archive', {}, diff).then(function(_item) {
                _item._autosave = null;
                return _item;
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
         * Test if an item is published
         *
         * @param {Object} item
         */
        this.isPublished = function isPublished(item) {
            return _.contains(['published', 'killed', 'scheduled', 'corrected'], item.state);
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

        /**
        * Link an item for takes.
        * @param {Object} item : Target Item
        * @param {string} [link_id]: If not provider it returns the new Linked item.
        * @param {string} [desk]: Desk for newly create item.
        */
        this.linkItem = function link(item, link_id, desk) {
            var data = {};
            if (link_id) {
                data.link_id = link_id;
            }

            if (desk) {
                data.desk = desk;
            }

            return api.save('archive_link', {}, data, item);
        };

        /**
        * Actions that it can perform on an item
        * @param {Object} item : item
        */
        this.itemActions = function(item) {
            var current_item = item && angular.isDefined(item.archive_item) ? item.archive_item : item;
            var user_privileges = privileges.privileges;
            var action = angular.extend({}, DEFAULT_ACTIONS);

            // takes packages are readonly.
            // killed item and item that have last publish action are readonly
            if ((angular.isUndefined(current_item) || angular.isUndefined(user_privileges)) ||
                (current_item.state === 'killed') ||
                (angular.isDefined(current_item.takes) && current_item.takes.state === 'killed')) {
                return action;
            }

            var is_read_only_state = _.contains(['spiked', 'scheduled', 'killed'], current_item.state) ||
            (angular.isDefined(current_item.package_type) && current_item.package_type === 'takes');

            var lockedByMe = !lock.isLocked(current_item);
            action.view = !lockedByMe;

            // new take should be on the text item that are closed or last take but not killed and doesn't have embargo.
            action.new_take = !is_read_only_state && (current_item.type === 'text' || current_item.type === 'preformatted') &&
                !current_item.embargo && !current_item.publish_schedule &&
                (angular.isUndefined(current_item.takes) || current_item.takes.last_take === current_item._id) &&
                (angular.isUndefined(current_item.more_coming) || !current_item.more_coming);

            // item is published state - corrected, published, scheduled, killed
            if (self.isPublished(current_item)) {
                //if not the last published version
                if ((angular.isDefined(item.archive_item) &&
                    item._current_version !== item.archive_item._current_version) ||
                    (this._versionToFetch && this._versionToFetch !== item._current_version)) {
                    return angular.extend({}, DEFAULT_ACTIONS);
                }

                action.view = true;
                if (current_item.state === 'scheduled') {
                    action.deschedule = true;
                } else if (current_item.state === 'published' || current_item.state === 'corrected') {
                    action.kill = user_privileges.kill && lockedByMe && !is_read_only_state;
                    action.correct = user_privileges.correct && lockedByMe && !is_read_only_state;
                }

                action.re_write = (_.contains(['published', 'corrected'], current_item.state) &&
                    _.contains(['text', 'preformatted'], current_item.type) && !current_item.embargo &&
                    (angular.isUndefined(current_item.more_coming) || !current_item.more_coming));

            } else {
                // production states i.e in_progress, routed, fetched, submitted.

                //if spiked
                if (current_item.state === 'spiked') {
                    action = angular.extend({}, DEFAULT_ACTIONS);
                    action.unspike = true;
                    return action;
                }

                action.save = current_item.state !== 'spiked';
                action.publish = !current_item.marked_for_not_publication &&
                        current_item.task && current_item.task.desk &&
                        user_privileges.publish && current_item.state !== 'draft';

                action.edit = !(current_item.type === 'composite' && current_item.package_type === 'takes') &&
                                current_item.state !== 'spiked' && lockedByMe;
                action.unspike = current_item.state === 'spiked' && user_privileges.unspike;
                action.spike = current_item.state !== 'spiked' && user_privileges.spike &&
                    (angular.isUndefined(current_item.takes) || current_item.takes.last_take === current_item._id);
                action.send = current_item._current_version > 0 && user_privileges.move;
            }

            //mark item for highlights
            action.mark_item = (current_item.task && current_item.task.desk &&
                !is_read_only_state && current_item.package_type !== 'takes' &&
                 user_privileges.mark_for_highlights);

            // allow all stories to be packaged if it doesn't have Embargo
            action.package_item = current_item.state !== 'spiked' && current_item.state !== 'scheduled' &&
                !current_item.embargo && current_item.package_type !== 'takes' &&
                current_item.state !== 'killed' && !current_item.publish_schedule;

            action.multi_edit = !is_read_only_state;

            //check for desk membership for edit rights.
            if (current_item.task && current_item.task.desk) {
                // in production

                action.duplicate = user_privileges.duplicate &&
                    !_.contains(['spiked', 'killed'], current_item.state) &&
                    (angular.isUndefined(current_item.package_type) || current_item.package_type !== 'takes');

                var desk = _.find(self.userDesks, {'_id': current_item.task.desk});
                if (!desk) {
                    action = angular.extend({}, DEFAULT_ACTIONS);
                }
            } else {
                // personal
                action.copy = true;
                action.view = false;
                action.package_item = false;
                action.new_take = false;
            }

            return action;
        };

        /**
         * Sometimes the fetched version and user selected version are different. Use this method to set the version
         * selected by user. This happens when user selects "Open" action.
         */
        this.setItemVersion = function(version) {
            this._versionToFetch = version;
        };

        /**
         * Check whether the item is a Take or not.
         * @param {object} item
         * @returns {boolean} True if a "Valid Take" else False
         */
        this.isTakeItem = function(item) {
            return (_.contains(['text', 'preformatted'], item.type) &&
                item.takes && item.takes.sequence > 1);
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

    ConfirmDirtyService.$inject = ['$window', '$q', '$filter', 'api', 'modal', 'gettext', '$interpolate'];
    function ConfirmDirtyService($window, $q, $filter, api, modal, gettext, $interpolate) {
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
        this.confirmPublish = function confirmPublish(action) {
            return modal.confirm(
                $interpolate(gettext('There are some unsaved changes, do you want to save it and {{ action }} now?'))({action: action}),
                gettext('Save changes?'),
                $interpolate(gettext('Save and {{ action }}'))({action: action}),
                gettext('Cancel')
            );
        };

        this.confirmSaveWork = function confirmSavework(msg) {
            return modal.confirm(
                $interpolate(gettext('Configuration has changed, {{ message }}. Would you like to save story to your workspace?'))
                ({message: msg})
            );
        };

        this.confirmSpellcheck = function confirmSpellcheck(msg) {
            return modal.confirm(
                $interpolate(gettext('You have {{ message }} spelling mistakes. Are you sure you want to continue?'))
                ({message: msg})
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

    ChangeImageController.$inject = ['$scope', 'gettext', 'notify', 'modal', '$q'];
    function ChangeImageController($scope, gettext, notify, modal, $q) {
        $scope.data = $scope.locals.data;
        $scope.preview = {};
        $scope.origPreview = {};
        $scope.data.cropData = {};
        $scope.data.isDirty = false;

        $scope.$watch('preview', function(newValue, oldValue) {
            if (newValue === oldValue) {
                $scope.origPreview = $scope.preview;
                return;
            }

            // During the initialisation of jcrop the preview object keeps changing and
            // new keys are being added to it. We want to ignore those changes and only
            // respond to those  that are actually caused by the changed crop coordinates.
            if (Object.keys(newValue).length === Object.keys(oldValue).length) {
                $scope.data.isDirty = true;
                return;
            }
        }, true);

        /*
        * Gets the crop coordinates, which was set in preview object during the onChange
        * event of jcrop
        */
        function getCropCoordinates(cropName) {
            var coordinates = {};
            var cropPoints  = $scope.preview[cropName];
            coordinates.CropLeft = Math.round(Math.min(cropPoints.cords.x, cropPoints.cords.x2));
            coordinates.CropRight = Math.round(Math.max(cropPoints.cords.x, cropPoints.cords.x2));
            coordinates.CropTop = Math.round(Math.min(cropPoints.cords.y, cropPoints.cords.y2));
            coordinates.CropBottom = Math.round(Math.max(cropPoints.cords.y, cropPoints.cords.y2));

            return coordinates;
        }

        /*
        * Serves for holding the crop coordinates
        */
        function recordCrops(cropName) {
            var obj = {};
            obj[cropName] = getCropCoordinates(cropName);
            _.extend($scope.data.cropData, obj);
        }

        /*
        * Records the coordinates for each crop sizes available and
        * notify the user and then resolve the activity.
        */
        $scope.done = function() {
            _.forEach($scope.data.cropsizes, function(cropsize) {
                recordCrops(cropsize.name);
            });
            notify.success(gettext('Crop changes have been recorded'));
            $scope.resolve($scope.data);
        };

        $scope.close = function() {
            if ($scope.data.isDirty) {
                modal.confirm(gettext('You have unsaved changes, do you want to continue?'))
                .then(function() { // Ok = continue w/o saving
                    $scope.data.isDirty = false;
                    $scope.preview = $scope.origPreview;
                    $scope.resolve($scope.data);
                });
            } else {
                $scope.reject();
            }
        };
    }

    AuthoringController.$inject = ['$scope', 'item', 'action', 'superdesk'];
    function AuthoringController($scope, item, action, superdesk) {
        $scope.origItem = item;
        $scope.action = action || 'edit';

        $scope.lock = function() {
            superdesk.intent('author', 'article', item);
        };
    }

    AuthoringDirective.$inject = [
        'superdesk',
        'superdeskFlags',
        'authoringWorkspace',
        'notify',
        'gettext',
        'desks',
        'authoring',
        'api',
        'session',
        'lock',
        'privileges',
        'content',
        '$location',
        'referrer',
        'macros',
        '$timeout',
        '$q',
        '$window',
        'modal',
        'archiveService'
    ];
    function AuthoringDirective(superdesk, superdeskFlags, authoringWorkspace, notify, gettext, desks, authoring, api, session, lock,
            privileges, content, $location, referrer, macros, $timeout, $q, $window, modal, archiveService) {
        return {
            link: function($scope, elem, attrs) {
                var _closing;

                $scope.privileges = privileges.privileges;
                $scope.dirty = false;
                $scope.views = {send: false};
                $scope.stage = null;
                $scope._editable = !!$scope.origItem._editable;
                $scope.isMediaType = _.contains(['audio', 'video', 'picture'], $scope.origItem.type);
                $scope.action = $scope.action || ($scope._editable ? 'edit' : 'view');
                $scope.itemActions = authoring.itemActions($scope.origItem);
                $scope.highlight = !!$scope.origItem.highlight;

                $scope.$watch('origItem', function(new_value, old_value) {
                    $scope.itemActions = null;
                    if (new_value) {
                        $scope.itemActions = authoring.itemActions(new_value);
                    }
                }, true);

                $scope._isInProductionStates = !authoring.isPublished($scope.origItem);
                $scope.origItem.sign_off = $scope.origItem.sign_off || $scope.origItem.version_creator;

                if ($scope.action === 'kill') {
                    api('content_templates').getById('kill').then(function(template) {
                        template = _.pick(template, _.keys(CONTENT_FIELDS_DEFAULTS));
                        var body = template.body_html;
                        if (body) {
                            // get the placeholders out of the template
                            var placeholders = _.words(body, /\${([\s\S]+?)}/g);
                            placeholders = _.map(placeholders, function(placeholder) {
                                return _.trim(placeholder, '${} ');
                            });

                            var compiled = _.template(body);
                            var args = {};

                            _.each(placeholders, function(placeholder) {
                                args[placeholder] = (placeholder !== 'dateline') ? $scope.origItem[placeholder] :
                                    $scope.origItem[placeholder].text.toUpperCase();
                            });
                            $scope.origItem.body_html = compiled(args);
                        }
                        _.each(template, function(value, key) {
                            if (!_.isEmpty(value)) {
                                if (key !== 'body_html') {
                                    $scope.origItem[key] = value;
                                }
                            }
                        });
                    });
                }

                $scope.$watch('item.marked_for_not_publication', function(newValue, oldValue) {
                    if (newValue !== oldValue) {
                        var item = _.create($scope.origItem);
                        $scope.dirty = true;
                        item.marked_for_not_publication = newValue;
                        $scope.itemActions = authoring.itemActions(item);
                    }
                });

                $scope.proofread = false;
                $scope.referrerUrl = referrer.getReferrerUrl();

                if ($scope.origItem.task && $scope.origItem.task.stage) {
                    if (archiveService.isLegal($scope.origItem)) {
                        $scope.deskName = $scope.origItem.task.desk;
                        $scope.stage = $scope.origItem.task.stage;
                    } else {
                        api('stages').getById($scope.origItem.task.stage)
                            .then(function(result) {
                                $scope.stage = result;
                            });

                        desks.fetchDeskById($scope.origItem.task.desk).then(function (desk) {
                            $scope.deskName = desk.name;
                        });
                    }
                }

                /*
                 * Open list of items in selected stage
                 */
                $scope.openStage = function openStage() {
                    desks.setWorkspace($scope.item.task.desk, $scope.item.task.stage);
                    superdesk.intent('view', 'content');
                };

                /**
                 * Start editing current item
                 */
                $scope.edit = function edit() {
                    authoringWorkspace.edit($scope.origItem);
                };

                /**
                 * Create a new version
                 */
                $scope.save = function() {
                    return authoring.save($scope.origItem, $scope.item).then(function(res) {
                        $scope.origItem = res;
                        $scope.dirty = false;
                        $scope.item = _.create($scope.origItem);
                        if (res.cropData) {
                            $scope.item.hasCrops = true;
                        }

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
                        } else if (response.status === 412) {
                            notifyPreconditionFailed();
                        } else {
                            notify.error(gettext('Error. Item not updated.'));
                        }
                    });
                };

                /**
                 * Export the list of highlights as a text item.
                 */
                $scope.exportHighlight = function(item) {
                    if ($scope.save_enabled()) {
                        modal.confirm(gettext('You have unsaved changes, do you want to continue.'))
                            .then(function() {
                                _exportHighlight(item._id);
                            }
                        );
                    } else {
                        _exportHighlight(item._id);
                    }
                };

                function _exportHighlight(_id) {
                    api.generate_highlights.save({}, {'package': _id})
                    .then(authoringWorkspace.edit, function(response) {
                        notify.error(gettext('Error creating highlight.'));
                    });
                }

                /**
                 * Invoked by validatePublishScheduleAndEmbargo() to validate the date and time values.
                 *
                 * @return {string} if the values are invalid then returns appropriate error message.
                 *         Otherwise empty string.
                 */
                function validateTimestamp(datePartOfTS, timePartOfTS, timestamp, fieldName) {
                    var errorMessage = '';

                    if (datePartOfTS && !timePartOfTS) {
                        errorMessage = gettext(fieldName + ' time is invalid!');
                    } else if (timePartOfTS && !datePartOfTS) {
                        errorMessage = gettext(fieldName + ' date is invalid!');
                    }

                    if (errorMessage === '' && timestamp) {
                        var schedule = new Date(timestamp);

                        if (!_.isDate(schedule)) {
                            errorMessage = gettext(fieldName + ' is not a valid date!');
                        } else if (!schedule.getTime()) {
                            errorMessage = gettext(fieldName + ' time is invalid!');
                        } else if (schedule < _.now()) {
                            if (fieldName !== 'Embargo' || $scope._isInProductionStates) {
                                errorMessage = gettext(fieldName + ' cannot be earlier than now!');
                            }
                        }
                    }

                    return errorMessage;
                }

                /**
                 * Validates the Embargo Date and Time and Publish Schedule Date and Time if they are set on the item.
                 *
                 * @return {boolean} true if valid, false otherwise.
                 */
                function validatePublishScheduleAndEmbargo(item) {
                    if (item.embargo && item.publish_schedule) {
                        notify.error(gettext('An Item can\'t have both Embargo and Publish Schedule.'));
                        return false;
                    }

                    var errorMessage;
                    if (item.embargo_date || item.embargo_time) {
                        errorMessage = validateTimestamp(item.embargo_date, item.embargo_time, item.embargo, 'Embargo');
                        if (errorMessage !== '') {
                            notify.error(errorMessage);
                            return false;
                        }
                    }

                    if (item.publish_schedule_date || item.publish_schedule_time) {
                        if (_.contains(['published', 'killed', 'corrected'], item.state)) {
                            return true;
                        }

                        errorMessage = validateTimestamp(item.publish_schedule_date, item.publish_schedule_time,
                            item.publish_schedule, 'Publish Schedule');
                        if (errorMessage !== '') {
                            notify.error(errorMessage);
                            return false;
                        }
                    }

                    return true;
                }

                function publishItem(orig, item) {
                    var action = $scope.action === 'edit' ? 'publish' : $scope.action;
                    authoring.publish(orig, item, action)
                    .then(function(response) {
                        if (response) {
                            if (angular.isDefined(response.data) && angular.isDefined(response.data._issues)) {
                                if (angular.isDefined(response.data._issues['validator exception'])) {

                                    var errors = response.data._issues['validator exception'];
                                    var modified_errors = errors.replace(/\[/g, '').replace(/\]/g, '').split(',');
                                    for (var i = 0; i < modified_errors.length; i++) {
                                        notify.error(modified_errors[i]);
                                    }

                                    if (errors.indexOf('9007') >= 0 || errors.indexOf('9009') >= 0) {
                                        authoring.open(item._id, true).then(function(res) {
                                            $scope.origItem = res;
                                            $scope.dirty = false;
                                            $scope.item = _.create($scope.origItem);
                                        });
                                    }
                                }
                            } else if (response.status === 412) {
                                notifyPreconditionFailed();
                            } else {
                                notify.success(gettext('Item published.'));
                                $scope.item = response;
                                $scope.dirty = false;
                                authoringWorkspace.close();
                            }
                        } else {
                            notify.error(gettext('Unknown Error: Item not published.'));
                        }
                    });
                }

                function notifyPreconditionFailed() {
                    notify.error(gettext('Item has changed since it was opened. ' +
                        'Please close and reopen the item to continue. ' +
                        'Regrettably, your changes cannot be saved.'));
                    $scope._editable = false;
                    $scope.dirty = false;
                }

                /**
                 * Depending on the item state one of the publish, correct, kill actions will be executed on the item
                 * in $scope.
                 */
                $scope.publish = function() {
                    if (validatePublishScheduleAndEmbargo($scope.item)) {
                        var message = 'publish';
                        if ($scope.action && $scope.action !== 'edit') {
                            message = $scope.action;
                        }

                        if ($scope.dirty && message === 'publish') {
                            //confirmation only required for publish
                            authoring.publishConfirmation($scope.origItem, $scope.item, $scope.dirty, message)
                            .then(function(res) {
                                if (res) {
                                    publishItem($scope.origItem, $scope.item);
                                }
                            }, function(response) {
                                notify.error(gettext('Error. Item not published.'));
                            });
                        } else {
                            publishItem($scope.origItem, $scope.item);
                        }
                    }
                };

                $scope.deschedule = function() {
                    $scope.item.publish_schedule = null;
                    return $scope.save();
                };

                /**
                 * Close an item - unlock
                 */
                $scope.close = function() {
                    _closing = true;
                    authoring.close($scope.item, $scope.origItem, $scope.save_enabled()).then(function () {
                        superdeskFlags.flags.hideMonitoring = false;
                        authoringWorkspace.close($scope.item);
                    });
                };

                /*
                 * Minimize an item
                 */
                $scope.minimize = function () {
                    authoringWorkspace.close();
                };

                $scope.closeOpenNew = function(createFunction, paramValue) {
                    _closing = true;
                    authoring.close($scope.item, $scope.origItem, $scope.dirty, true).then(function() {
                        createFunction(paramValue);
                    });
                };

                /**
                 * Called by the sendItem directive before send.
                 * If the $scope is dirty then save the item and then unlock the item.
                 * If the $scope is not dirty then unlock the item.
                 */
                $scope.beforeSend = function() {
                    $scope.sending = true;
                    if ($scope.dirty) {
                        return $scope.save()
                            .then(function() {
                               return lock.unlock($scope.origItem);
                           });
                    } else {
                        return lock.unlock($scope.origItem);
                    }
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
                    $scope._editable = $scope.action !== 'view' && authoring.isEditable($scope.origItem);
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

                // call the function to unlock and lock the story for editing.
                $scope.unlock = function() {
                    $scope.unlockClicked = true;
                    lock.unlock($scope.item).then(function(unlocked_item) {
                        $scope.edit(unlocked_item);
                    });
                };

                $scope.openAction = function(action) {
                    if (action === 'correct') {
                        authoringWorkspace.correct($scope.item);
                    } else if (action === 'kill') {
                        authoringWorkspace.kill($scope.item);
                    }
                };

                $scope.isLockedByMe = function() {
                    return lock.isLockedByMe($scope.item);
                };

                $scope.autosave = function(item) {
                    $scope.dirty = true;
                    return authoring.autosave(item);
                };

                function refreshItem() {
                    authoring.open($scope.item._id, true)
                        .then(function(item) {
                            $scope.origItem = item;
                            $scope.dirty = false;
                            $scope.closePreview();
                            $scope.item._editable = $scope._editable;
                        });
                }

                // init
                $scope.content = content;
                $scope.closePreview();
                $scope.$on('savework', function(e, msg) {
                    var changeMsg = msg;
                    authoring.saveWorkConfirmation($scope.origItem, $scope.item, $scope.dirty, changeMsg)
                    .then(function(res) {
                        desks.setCurrentDeskId(null);
                        $location.url('/workspace/content');
                        referrer.setReferrerUrl('/workspace/content');
                    })
                    ['finally'](function() {
                        $window.location.reload(true);
                    });
                });
                $scope.$on('item:lock', function(_e, data) {
                    if ($scope.item._id === data.item && !_closing &&
                        session.sessionId !== data.lock_session) {
                        authoring.lock($scope.item, data.user);
                    }
                });

                $scope.$on('item:unlock', function(_e, data) {
                    if ($scope.item._id === data.item && !_closing &&
                        session.sessionId !== data.lock_session) {
                        authoring.unlock($scope.item, data.user);
                        $scope._editable = $scope.item._editable = false;
                        $scope.origItem._locked = $scope.item._locked = false;
                        $scope.origItem.lock_session = $scope.item.lock_session = null;
                        $scope.origItem.lock_user = $scope.item.lock_user = null;
                    }
                });

                $scope.$on('item:updated', function(_e, data) {
                    if (data.item === $scope.origItem._id && $scope.action === 'view') {
                        refreshItem();
                    }
                });

                $scope.$on('item:publish:wrong:format', function(_e, data) {
                    if (data.item === $scope.item._id) {
                        notify.error(gettext('No formatters found for ') + data.formats.join(',') +
                            ' while publishing item having story name ' + data.unique_name);
                    }
                });

                macros.setupShortcuts($scope);
            }
        };
    }

    function AuthoringTopbarDirective() {
        return {
            templateUrl: 'scripts/superdesk-authoring/views/authoring-topbar.html',
            link: function(scope) {
                scope.saveDisabled = false;
                scope.saveTopbar = function(item) {
                    scope.saveDisabled = true;
                    return scope.save(item)
                    ['finally'](function() {
                        scope.saveDisabled = false;
                    });
                };
            }
        };
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
        return data.replace(/<br[^>]*>/gi, '&nbsp;').replace(/<\/?[^>]+><\/?[^>]+>/gi, ' ')
            .replace(/<\/?[^>]+>/gi, '').trim().replace(/&nbsp;/g, ' ');
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
        var THEME_DEFAULT = 'default';

        service.availableThemes = [
            {
                cssClass: '',
                label: 'Default',
                key: 'default'
            },
            {
                cssClass: 'dark-theme',
                label: 'Dark',
                key: 'dark'
            },
            {
                cssClass: 'natural-theme',
                label: 'Natural',
                key: 'natural'
            },
            {
                cssClass: 'dark-blue-theme',
                label: 'Dark blue',
                key: 'dark-blue'
            },
            {
                cssClass: 'dark-turquoise-theme',
                label: 'Dark turquoise',
                key: 'dark-turquoise'
            },
            {
                cssClass: 'dark-khaki-theme',
                label: 'Dark khaki',
                key: 'dark-khaki'
            },
            {
                cssClass: 'dark-theme-mono',
                label: 'Dark monospace',
                key: 'dark-mono'
            }
        ];

        service.save = function(key, themeScope) {
            return preferencesService.get().then(function(result) {
                result[PREFERENCES_KEY][key] = themeScope[key].key + (themeScope.large[key] ? '-large' : '');
                return preferencesService.update(result);
            });
        };

        service.get = function(key) {
            return preferencesService.get().then(function(result) {
                var theme = result[PREFERENCES_KEY] && result[PREFERENCES_KEY][key] ? result[PREFERENCES_KEY][key] : THEME_DEFAULT;
                return theme;
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
                scope.large = {};
                authThemes.get('theme').then(function(theme) {
                    var selectedTheme = _.find(authThemes.availableThemes, {key: themeKey(theme)});
                    scope.theme = selectedTheme;
                    scope.large.theme = themeLarge(theme);
                    applyTheme('theme');
                });
                authThemes.get('proofreadTheme').then(function(theme) {
                    var selectedTheme = _.find(authThemes.availableThemes, {key: themeKey(theme)});
                    scope.proofreadTheme = selectedTheme;
                    scope.large.proofreadTheme = themeLarge(theme);
                    applyTheme('proofreadTheme');
                });

                /*
                 * Changing predefined themes for proofread and normal mode
                 *
                 * @param {string} key Type of theme (proofread or normal)
                 * @param {object} theme New theme
                 */
                scope.changeTheme = function(key, theme) {
                    scope[key] = theme;
                    authThemes.save(key, scope);
                    applyTheme(key);
                };

                /*
                 * Changing predefined size for proofread and normal mode
                 *
                 * @param {string} key Type of theme (proofread or normal)
                 * @param {object} size New size
                 */
                scope.changeSize = function(key, size) {
                    scope.large[key] = size;
                    authThemes.save(key, scope);
                    applyTheme(key);
                };

                /*
                 * Applying a theme for currently selected mode
                 *
                 * @param {string} key Type of theme (proofread or normal)
                 */
                function applyTheme(key) {
                    if (scope.key === key) {
                        elem.closest('.page-content-container')
                            .children('.theme-container')
                            .attr('class', DEFAULT_CLASS)
                            .addClass(scope[key].cssClass)
                            .addClass(scope.large[key] && 'large-text');
                    }
                }

                function themeKey(theme){
                    return theme.indexOf('-large') !== -1 ? theme.slice(0, theme.indexOf('-large')) : theme;
                }

                function themeLarge(theme){
                    return theme.indexOf('-large') !== -1 ? true : false;
                }
            }
        };
    }
    SendItem.$inject = ['$q', 'api', 'desks', 'notify', 'authoringWorkspace', 'superdeskFlags',
        '$location', 'macros', '$rootScope', 'authoring', 'send', 'spellcheck', 'confirm'];
    function SendItem($q, api, desks, notify, authoringWorkspace, superdeskFlags,
        $location, macros, $rootScope, authoring, send, spellcheck, confirm) {
        return {
            scope: {
                item: '=',
                view: '=',
                _beforeSend: '=beforeSend',
                _editable: '=editable',
                _publish: '=publish',
                _action: '=action',
                mode: '@'
            },
            templateUrl: 'scripts/superdesk-authoring/views/send-item.html',
            link: function sendItemLink(scope, elem, attrs) {
                scope.mode = scope.mode || 'authoring';
                scope.desks = null;
                scope.stages = null;
                scope.macros = null;
                scope.task = null;
                scope.selectedDesk = null;
                scope.selectedStage = null;
                scope.selectedMacro = null;
                scope.beforeSend = scope._beforeSend || $q.when;

                scope.$watch('item', activateItem);
                scope.$watch(send.getConfig, activateConfig);

                function activateConfig(config, oldConfig) {
                    if (config !== oldConfig) {
                        scope.isActive = !!config;
                        scope.item = scope.isActive ? {} : null;
                        scope.config = config;
                        activate();
                    }
                }

                function activateItem(item) {
                    if (scope.mode === 'monitoring') {
                        superdeskFlags.flags.fetching = !!item;
                    }

                    scope.isActive = !!item;
                    activate();
                }

                function activate() {
                    if (scope.isActive) {
                        desks.initialize()
                            .then(fetchDesks)
                            .then(fetchStages)
                            .then(fetchMacros)
                            .then(initializeItemActions);
                    }
                }

                scope.close = function() {
                    if (scope.mode === 'monitoring') {
                        superdeskFlags.flags.fetching = false;
                    }

                    if (scope.$parent.views) {
                        scope.$parent.views.send = false;
                    } else {
                        scope.item = null;
                    }

                    $location.search('fetch', null);

                    if (scope.config) {
                        scope.config.reject();
                    }
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

                scope.send = function (open) {
                    var spellcheckErrors = spellcheck.countErrors();
                    if (scope.mode === 'authoring' && spellcheckErrors > 0) {
                        confirm.confirmSpellcheck(spellcheckErrors)
                                .then(angular.bind(this, function send() {
                                    return runSend(open);
                                }), function (err) { // cancel
                                    return false;
                                });
                    } else {
                        return runSend(open);
                    }
                };

                /*
                 * Returns true if Destination field and Send button needs to be displayed, false otherwise.
                 * @returns {Boolean}
                 */
                scope.showSendButtonAndDestination = function () {
                    if (scope.itemActions) {
                        return scope.mode === 'ingest' ||
                                scope.mode === 'monitoring' ||
                                (scope.mode === 'authoring' && scope.isSendEnabled() && scope.itemActions.send);
                    }
                };

                /*
                 * Returns true if Send and Send and Continue button needs to be disabled, false othervise.
                 * @returns {Boolean}
                 */
                scope.disableSendButton = function () {
                    if (scope.item && scope.item.task) {
                        return !scope.selectedDesk ||
                                (scope.mode !== 'ingest' && scope.selectedStage._id === scope.item.task.stage);
                    }
                };

                /**
                 * Returns true if Publish Schedule needs to be displayed, false otherwise.
                 */
                scope.showPublishSchedule = function() {
                    return scope.mode !== 'ingest' && scope.item && scope.item.type !== 'composite' &&
                        !scope.item.embargo_date && !scope.item.embargo_time &&
                        !authoring.isTakeItem(scope.item) &&
                        ['published', 'killed', 'corrected'].indexOf(scope.item.state) === -1;
                };

                /**
                 * Returns true if Embargo needs to be displayed, false otherwise.
                 */
                scope.showEmbargo = function() {
                    var prePublishCondition = scope.mode !== 'ingest' && scope.item &&
                        scope.item.type !== 'composite' && !scope.item.publish_schedule_date &&
                        !scope.item.publish_schedule_time && !authoring.isTakeItem(scope.item);

                    if (prePublishCondition && authoring.isPublished(scope.item)) {
                        return scope.item.embargo;
                    }

                    return prePublishCondition;
                };

                /**
                 * Returns true if Embargo needs to be displayed, false otherwise.
                 */
                scope.isEmbargoEditable = function() {
                    return scope.item && scope.item._editable && !authoring.isPublished(scope.item);
                };

                function runSend(open) {
                    scope.item.sendTo = true;
                    var deskId = scope.selectedDesk._id;
                    var stageId = scope.selectedStage._id || scope.selectedDesk.incoming_stage;

                    if (scope.mode === 'authoring') {
                        return sendAuthoring(deskId, stageId, scope.selectedMacro);
                    } else if (scope.mode === 'archive') {
                        return sendContent(deskId, stageId, scope.selectedMacro, open);
                    } else if (scope.config) {
                        return scope.config.resolve({
                            desk: deskId,
                            stage: stageId,
                            macro: scope.selectedMacro ? scope.selectedMacro.name : null,
                            open: open
                        });
                    } else if (scope.mode === 'ingest') {
                        return sendIngest(deskId, stageId, scope.selectedMacro, open);
                    }
                }

                scope.canSendAndContinue = function() {
                    return !authoring.isPublished(scope.item) && _.contains(['text', 'preformatted'], scope.item.type);
                };

                /**
                 * Returns true if 'send' button should be displayed. Otherwise, returns false.
                 * @return {boolean}
                 */
                scope.isSendEnabled = function() {
                    return !authoring.isPublished(scope.item);
                };

                /**
                 * Send the current item (take) to different desk or stage and create a new take.
                 * If publish_schedule is set then the user cannot schedule the take.
                 * Fails if user has set Embargo on the item.
                 */
                scope.sendAndContinue = function () {
                    // cannot schedule takes.
                    if (scope.item && scope.item.publish_schedule) {
                        notify.error(gettext('Takes cannot be scheduled.'));
                        return;
                    }

                    if (scope.item && scope.item.embargo) {
                        notify.error(gettext('Takes cannot have Embargo.'));
                        return;
                    }

                    var spellcheckErrors = spellcheck.countErrors();
                    if (spellcheckErrors > 0) {
                        confirm.confirmSpellcheck(spellcheckErrors)
                                .then(angular.bind(this, function send() {
                                    return runSendAndContinue();
                                }), function (err) { // cancel
                                    return false;
                                });
                    } else {
                        return runSendAndContinue();
                    }
                };

                /**
                 * Send the current item to different desk or stage and create a new take and open for editing.
                 */
                function runSendAndContinue() {
                    var deskId = scope.selectedDesk._id;
                    var stageId = scope.selectedStage._id || scope.selectedDesk.incoming_stage;

                    scope.item.more_coming = true;
                    scope.item.sendTo = true;
                    return sendAuthoring(deskId, stageId, scope.selectedMacro, true)
                        .then(function() {
                            var itemDeskId = null;
                            if (scope.item.task && scope.item.task.desk) {
                                itemDeskId = scope.item.task.desk;
                            }
                            return authoring.linkItem(scope.item, null, itemDeskId);
                        })
                        .then(function (item) {
                            authoringWorkspace.close();
                            notify.success(gettext('New take created.'));
                            authoringWorkspace.edit(item);
                        }, function(err) {
                            notify.error(gettext('Failed to send and continue.'));
                        });
                }

                function runMacro(item, macro) {
                    if (macro) {
                        return macros.call(macro, item, true);
                    }

                    return $q.when(item);
                }

                function sendAuthoring(deskId, stageId, macro, sendAndContinue) {
                    var deferred;

                    if (sendAndContinue) {
                        deferred = $q.defer();
                    }

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
                            return api.save('move', {}, {task: {desk: deskId, stage: stageId}}, scope.item);
                        })
                        .then(function(value) {
                            notify.success(gettext('Item sent.'));
                            if (sendAndContinue) {
                                return deferred.resolve();
                            } else {
                                authoringWorkspace.close();
                            }
                        }, function(err) {
                            if (angular.isDefined(err.data._message)) {
                                notify.error(err.data._message);
                            } else {
                                if (angular.isDefined(err.data._issues['validator exception'])) {
                                    notify.error(err.data._issues['validator exception']);
                                }
                            }

                            if (sendAndContinue) {
                                return deferred.reject(err);
                            }
                        });
                    });

                    if (sendAndContinue) {
                        return deferred.promise;
                    }
                }

                function sendContent(deskId, stageId, macro, open) {
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
                        scope.close();
                        if (open) {
                            $location.url('/authoring/' + finalItem._id);
                        } else {
                            $rootScope.$broadcast('item:fetch');
                        }
                    });
                }

                function sendIngest(deskId, stageId, macro, open) {
                    return send.oneAs(scope.item, {
                        desk: deskId,
                        stage: stageId,
                        macro: macro ? macro.name : macro
                    }).then(function(finalItem) {
                        notify.success(gettext('Item fetched.'));
                        if (open) {
                            authoringWorkspace.edit(finalItem);
                        } else {
                            $rootScope.$broadcast('item:fetch');
                        }
                    });
                }

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

                        var stage = null;

                        if (scope.item.task && scope.item.task.stage) {
                            stage = _.find(scope.stages, {_id: scope.item.task.stage});
                        }

                        if (!stage) {
                            stage = _.find(scope.stages, {_id: scope.selectedDesk.incoming_stage});
                        }

                        scope.selectedStage = stage;
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

                /**
                 * The itemActions defined in parent scope (Authoring Directive) is made accessible via this method.
                 * scope.$parent isn't used as send-item directive is used in multiple places and has different
                 * hierarchy.
                 */
                function initializeItemActions() {
                    scope.itemActions = authoring.itemActions(scope.item);
                }
            }
        };
    }

    ArticleEditDirective.$inject = ['autosave', 'authoring', 'metadata', 'session', '$filter', '$timeout',
    'superdesk', 'notify', 'gettext'];
    function ArticleEditDirective(autosave, authoring, metadata, session, $filter, $timeout, superdesk, notify, gettext) {
        return {
            templateUrl: 'scripts/superdesk-authoring/views/article-edit.html',
            link: function(scope) {
                var DEFAULT_ASPECT_RATIO = 4 / 3;
                scope.limits = authoring.limits;
                scope.toggleDetails = true;
                scope.errorMessage = null;
                var mainEditScope = scope.$parent.$parent;

                /* Start: Dateline related properties */

                scope.monthNames = {'Jan': '0', 'Feb': '1', 'Mar': '2', 'Apr': '3', 'May': '4', 'Jun': '5',
                                    'Jul': '6', 'Aug': '7', 'Sept': '8', 'Oct': '9', 'Nov': '10', 'Dec': '11'};
                scope.datelineMonth = '';
                scope.datelineDay = '';

                /* End: Dateline related properties */

                /* Creates a copy of dateline object from item.__proto__.dateline */
                scope.$watch('item', function(item) {
                    if (item) {
                        var updates = {dateline: {}};
                        if (item.dateline) {
                            updates.dateline = _.pick(item.dateline, ['source', 'date', 'located', 'text']);
                            if (item.dateline.located) {
                                var monthAndDay = $filter('formatDatelineToMMDD')(item.dateline.date, item.dateline.located);
                                scope.datelineMonth = monthAndDay.month;
                                scope.datelineDay = monthAndDay.day;
                                scope.resetNumberOfDays(false);
                            }
                        }

                        _.extend(item, updates);
                    }
                });

                metadata.initialize().then(function() {
                    scope.item.hasCrops = false;
                    scope.metadata = metadata.values;
                    scope.item.hasCrops = scope.metadata.crop_sizes.some(function (crop) {
                        return scope.item.renditions[crop.name];
                    });
                });

                /**
                 * Invoked by the directive after updating the property in item. This method is responsible for updating
                 * the properties dependent on dateline.
                 */
                scope.updateDateline = function(item, city) {
                    if (city === '') {
                        item.dateline.located = null;
                        item.dateline.text = '';

                        scope.datelineMonth = '';
                        scope.datelineDay = '';
                    } else {
                        var monthAndDay = $filter('formatDatelineToMMDD')(item.dateline.date, item.dateline.located);

                        scope.datelineMonth = monthAndDay.month;
                        scope.datelineDay = monthAndDay.day;
                        scope.resetNumberOfDays(false);

                        item.dateline.text = $filter('formatDatelineToLocMMMDDSrc')(item.dateline.located,
                            _.findKey(scope.monthNames, function(m) { return m === scope.datelineMonth; }),
                            scope.datelineDay, item.dateline.source);
                    }
                };

                /**
                 * Invoked when user changes a month in the datelineMonth.
                 * Populates the datelineDay field with the days in the selected month.
                 *
                 * @param {Boolean} resetDatelineDate if true resets the dateline.date to be relative to selected date.
                 */
                scope.resetNumberOfDays = function(resetDatelineDate) {
                    if (scope.datelineMonth !== '') {
                        scope.daysInMonth = $filter('daysInAMonth')(parseInt(scope.datelineMonth));

                        if (resetDatelineDate) {
                            scope.modifyDatelineDate();
                        }
                    } else {
                        scope.daysInMonth = [];
                        scope.datelineDay = '';
                    }
                };

                /**
                 * Invoked when user selects a different day in dateline day list. This method calculates the
                 * relative UTC based on the new values of month and day and sets to dateline.date.
                 */
                scope.modifyDatelineDate = function() {
                    if (scope.datelineMonth !== '' && scope.datelineDay !== '') {
                        scope.item.dateline.date = $filter('relativeUTCTimestamp')(scope.item.dateline.located,
                                parseInt(scope.datelineMonth), parseInt(scope.datelineDay));

                        scope.item.dateline.text = $filter('formatDatelineToLocMMMDDSrc')(scope.item.dateline.located,
                            _.findKey(scope.monthNames, function(m) { return m === scope.datelineMonth; }),
                            scope.datelineDay, scope.item.dateline.source);

                        autosave.save(scope.item);
                    }
                };

                /**
                 * Function to evaluate aspect ratio attribute in advance to provide in
                 * proper decimal format required by jCrop.
                 */
                scope.evalAspectRatio = function(ar) {
                    var parts = ar.split('-').map(_.partial(parseInt, _, 10));
                    var result = parts[0] / parts[1];

                    if (isNaN(result) || !isFinite(result)) {
                        scope.errorMessage = 'Error: Given Aspect ratio was not valid, using default: ' + DEFAULT_ASPECT_RATIO;
                        return DEFAULT_ASPECT_RATIO;
                    } else {
                        scope.errorMessage = null;
                        return result;
                    }
                };

                scope.applyCrop = function() {
                    var ar = {};
                    scope.item.cropsizes = scope.metadata.crop_sizes;
                    _.forEach(scope.item.cropsizes, function(cropsizes) {
                        ar = {aspectRatio: scope.evalAspectRatio(cropsizes.name)};
                        _.extend(_.filter(scope.item.cropsizes, {name: cropsizes.name})[0], ar);
                    });

                    superdesk.intent('edit', 'crop',  scope.item).then(function(data) {
                        if (!mainEditScope.dirty) {
                            mainEditScope.dirty = data.isDirty;
                        }
                        var orig = _.create(data.renditions);
                        var diff = data.cropData;
                        scope.item.renditions = _.merge(orig, diff);
                    });
                };
            }
        };
    }

    angular.module('superdesk.authoring', [
            'superdesk.menu',
            'superdesk.editor',
            'superdesk.activity',
            'superdesk.authoring.widgets',
            'superdesk.authoring.metadata',
            'superdesk.authoring.comments',
            'superdesk.authoring.versioning',
            'superdesk.authoring.versioning.versions',
            'superdesk.authoring.versioning.history',
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
        .service('authoringWorkspace', AuthoringWorkspaceService)

        .directive('sdDashboardCard', DashboardCard)
        .directive('sdSendItem', SendItem)
        .directive('sdCharacterCount', CharacterCount)
        .directive('sdWordCount', WordCount)
        .directive('sdThemeSelect', ThemeSelectDirective)
        .directive('sdArticleEdit', ArticleEditDirective)
        .directive('sdAuthoring', AuthoringDirective)
        .directive('sdAuthoringTopbar', AuthoringTopbarDirective)
        .directive('sdAuthoringContainer', AuthoringContainerDirective)
        .directive('sdAuthoringEmbedded', AuthoringEmbeddedDirective)
        .directive('sdHeaderInfo', headerInfoDirective)

        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('authoring', {
                    category: '/authoring',
                    href: '/authoring/:_id',
                    when: '/authoring/:_id',
                    label: gettext('Authoring'),
                    templateUrl: 'scripts/superdesk-authoring/views/authoring.html',
                    topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
                    sideTemplateUrl: 'scripts/superdesk-workspace/views/workspace-sidenav.html',
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
                .activity('edit.item', {
                    label: gettext('Edit'),
                    priority: 10,
                    icon: 'pencil',
                    keyboardShortcut: 'ctrl+e',
                    controller: ['data', 'authoringWorkspace', function(data, authoringWorkspace) {
                        authoringWorkspace.edit(data.item ? data.item : data);
                    }],
                    filters: [
                        {action: 'list', type: 'archive'},
                        {action: 'edit', type: 'item'}
                    ],
                    additionalCondition: ['authoring', 'item', function(authoring, item) {
                        return authoring.itemActions(item).edit;
                    }]
                })
                .activity('kill.text', {
                    label: gettext('Kill item'),
                    priority: 100,
                    icon: 'remove',
                    group: 'corrections',
                    controller: ['data', 'authoringWorkspace', function(data, authoringWorkspace) {
                        authoringWorkspace.kill(data.item);
                    }],
                    filters: [{action: 'list', type: 'archive'}],
                    additionalCondition:['authoring', 'item', function(authoring, item) {
                        return authoring.itemActions(item).kill;
                    }],
                    privileges: {kill: 1}
                })
                .activity('correct.text', {
                    label: gettext('Correct item'),
                    priority: 100,
                    icon: 'pencil',
                    group: 'corrections',
                    controller: ['data', 'authoringWorkspace', function(data, authoringWorkspace) {
                        authoringWorkspace.correct(data.item);
                    }],
                    filters: [{action: 'list', type: 'archive'}],
                    additionalCondition:['authoring', 'item', function(authoring, item) {
                        return authoring.itemActions(item).correct;
                    }],
                    privileges: {correct: 1}
                })
                .activity('view.item', {
                    label: gettext('Open'),
                    priority: 2000,
                    icon: 'fullscreen',
                    keyboardShortcut: 'ctrl+o',
                    controller: ['data', 'authoringWorkspace', function(data, authoringWorkspace) {
                        authoringWorkspace.view(data.item || data);
                    }],
                    filters: [
                        {action: 'list', type: 'archive'},
                        {action: 'list', type: 'legal_archive'},
                        {action: 'view', type: 'item'}
                    ],
                    additionalCondition:['authoring', 'item', function(authoring, item) {
                        return authoring.itemActions(item).view;
                    }]
                })
                .activity('edit.crop', {
                    label: gettext('EDIT CROP'),
                    modal: true,
                    cssClass: 'upload-avatar modal-static modal-responsive',
                    controller: ChangeImageController,
                    templateUrl: 'scripts/superdesk-authoring/views/change-image.html',
                    filters: [{action: 'edit', type: 'crop'}]
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

    AuthoringContainerDirective.$inject = ['authoring', 'authoringWorkspace'];
    function AuthoringContainerDirective(authoring, authoringWorkspace) {

        function AuthoringContainerController() {
            var self = this;

            this.state = {};

            /**
             * Start editing item using given action mode
             *
             * @param {string} item
             * @param {string} action
             */
            this.edit = function(item, action) {
                self.item = item;
                self.action = action;
                self.state.opened = !!item;
            };
        }

        return {
            controller: AuthoringContainerController,
            controllerAs: 'authoring',
            templateUrl: 'scripts/superdesk-authoring/views/authoring-container.html',
            scope: {},
            require: 'sdAuthoringContainer',
            link: function(scope, elem, attrs, ctrl) {
                scope.$watch(authoringWorkspace.getState, function(state) {
                    if (state) {
                        ctrl.edit(null, null);
                        // do this in next digest cycle so that it can
                        // destroy authoring/packaging-embedded in current cycle
                        scope.$applyAsync(function() {
                            ctrl.edit(state.item, state.action);
                        });
                    }
                });
            }
        };
    }

    AuthoringEmbeddedDirective.$inject = [];
    function AuthoringEmbeddedDirective() {
        return {
            templateUrl: 'scripts/superdesk-authoring/views/authoring.html',
            scope: {
                origItem: '=item',
                action: '='
            }
        };
    }

    headerInfoDirective.$inject = ['familyService', 'authoringWidgets', 'authoring', 'archiveService'];
    function headerInfoDirective(familyService, authoringWidgets, authoring, archiveService) {
        return {
            templateUrl: 'scripts/superdesk-authoring/views/header-info.html',
            require: '^sdAuthoringWidgets',
            link: function (scope, elem, attrs, WidgetsManagerCtrl) {
                scope.$watch('item', function (item) {
                    if (!item) {
                        return;
                    }

                    scope.loaded = true;

                    if (!archiveService.isLegal(scope.item)) {
                        // Related Items
                        if (scope.item.slugline) {
                            archiveService.getRelatedItems(scope.item.slugline).then(function(items) {
                                scope.relatedItems = items;
                            });
                        }

                        var relatedItemWidget = _.filter(authoringWidgets, function (widget) {
                            return widget._id === 'related-item';
                        });

                        scope.activateWidget = function () {
                            WidgetsManagerCtrl.activate(relatedItemWidget[0]);
                        };
                    }

                });
            }
        };
    }

    AuthoringWorkspaceService.$inject = ['$location', 'superdeskFlags', 'authoring'];
    function AuthoringWorkspaceService($location, superdeskFlags, authoring) {
        this.item = null;
        this.action = null;
        this.state = null;

        var self = this;

        /**
         * Open item for editing
         *
         * @param {Object} item
         * @param {string} action
         */
        this.edit = function(item, action) {
            if (item) {
                authoringOpen(item._id, action || 'edit', item._type || null);
            } else {
                self.close();
            }
        };

        /**
         * Open an item in readonly mode without locking it
         *
         * @param {Object} item
         */
        this.view = function(item) {
            authoring.setItemVersion(item._current_version);
            self.edit(item, 'view');
        };

        /**
         * Stop editing
         */
        this.close = function() {
            self.item = null;
            self.action = null;
            saveState();
        };

        /**
         * Kill an item
         *
         * @param {Object} item
         */
        this.kill = function(item) {
            self.edit(item, 'kill');
        };

        /**
         * Correct an item
         *
         * @param {Object} item
         */
        this.correct = function(item) {
            self.edit(item, 'correct');
        };

        /**
         * Get edited item
         *
         * return {Object}
         */
        this.getItem = function() {
            return self.item;
        };

        /**
         * Get current action
         *
         * @return {string}
         */
        this.getAction = function() {
            return self.action;
        };

        /**
         * Get current state
         *
         * @return {Object}
         */
        this.getState = function() {
            return self.state;
        };

        /**
         * Save current item/action state into $location so that it can be
         * used on page reload
         */
        function saveState() {
            $location.search('item', self.item ? self.item._id : null);
            $location.search('action', self.action);
            superdeskFlags.flags.authoring = !!self.item;
            self.state = {item: self.item, action: self.action};
        }

        /**
         * On load try to fetch item set in url
         */
        function init() {
            if ($location.search().item && $location.search().action in self) {
                authoringOpen($location.search().item, $location.search().action);
            }
        }

        /**
         * Fetch item by id and start editing it
         */
        function authoringOpen(itemId, action, repo) {
            return authoring.open(itemId, action === 'view', repo)
                .then(function(item) {
                    self.item = item;
                    self.action = action;
                })
                .then(saveState);
        }

        init();
    }
})();
