(function() {
    'use strict';

    /**
     * Bussiness logic layer, should be used instead of resource
     */
    UsersService.$inject = ['api', '$q'];
    function UsersService(api, $q) {

        var STATUS_INACTIVE = 'inactive',
            STATUS_ACTIVE = 'active';

        this.usernamePattern = /^[A-Za-z0-9_.'-]+$/;
        this.phonePattern = /^(?:(?:0?[1-9][0-9]{8})|(?:(?:\+|00)[1-9][0-9]{9,11}))$/;

        /**
         * Save user with given data
         *
         * @param {Object} user
         * @param {Object} data
         * @returns {Promise}
         */
        this.save = function save(user, data) {
            return api.save('users', user, data)
                .then(function(updates) {
                    angular.extend(user, data);
                    angular.extend(user, updates);
                    return user;
                });
        };

        /**
         * Change user password
         *
         * @param {Object} user
         * @param {string} oldPassword
         * @param {string} newPassword
         * @returns {Promise}
         */
        this.changePassword = function(user, oldPassword, newPassword) {
            console.error('change password not implemented');
            return $q.reject();
        };

        /**
         * Test if user is active
         */
        this.isActive = function isActive(user) {
            return user && !user.status || user.status !== STATUS_INACTIVE;
        };

        /**
         * Toggle user status
         */
        this.toggleStatus = function toggleStatus(user, active) {
            return this.save(user, {status: active ? STATUS_ACTIVE : STATUS_INACTIVE});
        };
    }

    /**
     * Service for fetching users with caching.
     * Ideally, should be used app-wide.
     */
    UserListService.$inject = ['api', '$q', '$cacheFactory'];
    function UserListService(api, $q, $cacheFactory) {

        var userservice = {};

        var cache = $cacheFactory('userList');

        var DEFAULT_CACHE_KEY = '_nosearch';
        var DEFAULT_PAGE = 1;
        var DEFAULT_PER_PAGE = 20;

        /**
         * Fetches and caches users, or returns from the cache.
         *
         * @param {String} search
         * @param {Integer} page (Shouldn't be used at the moment)
         * @param {Integer} perPage
         * @returns {Promise}
         */
        userservice.get = function(search, page, perPage) {
            page = page || DEFAULT_PAGE;
            var key = search || DEFAULT_CACHE_KEY;
            perPage = perPage || DEFAULT_PER_PAGE;
            key = buildKey(key, page, perPage);

            var value = cache.get(key);
            if (value) {
                return $q.when(value);
            } else {
                var criteria = {
                    max_results: perPage
                };
                if (search) {
                    criteria.where = JSON.stringify({
                        '$or': [
                            {username: {'$regex': search, '$options': '-i'}},
                            {first_name: {'$regex': search, '$options': '-i'}},
                            {last_name: {'$regex': search, '$options': '-i'}},
                            {email: {'$regex': search, '$options': '-i'}}
                        ]
                    });
                }

                return api('users').query(criteria)
                .then(function(result) {
                    cache.put(key, result);
                    return result;
                });
            }
        };

        /**
         * Fetch single user from default cache, or make new api call
         *
         * @param {String} id of user
         * @returns {Promise}
         */
        userservice.getUser = function(id) {
            var default_cache = buildKey(DEFAULT_CACHE_KEY, DEFAULT_PAGE);

            var value = cache.get(default_cache);
            if (value) {
                var user = _.find(value._items, {_id: id});
                if (user) {
                    return $q.when(user);
                }
            }

            return api('users').getById(id)
            .then(function(result) {
                return result;
            });

        };

        function buildKey(key, page, perPage) {
            return key + '_' + page + '_' + perPage;
        }

        return userservice;
    }

    UserListController.$inject = ['$scope', '$location', 'api'];
    function UserListController($scope, $location, api) {
        $scope.maxResults = 25;

        $scope.selected = {user: null};
        $scope.createdUsers = [];

        $scope.preview = function(user) {
            $scope.selected.user = user;
        };

        $scope.createUser = function() {
            $scope.preview({});
        };

        $scope.closePreview = function() {
            $scope.preview(null);
        };

        $scope.afterDelete = function(data) {
            if ($scope.selected.user && data.item && data.item.href === $scope.selected.user.href) {
                $scope.selected.user = null;
            }
            fetchUsers(getCriteria());
        };

        // make sure saved user is presented in the list
        $scope.render = function(user) {
            if (_.find($scope.users._items, function(item) {
                return item._links.self.href === user._links.self.href;
            })) {
                return;
            }

            if (_.find($scope.createdUsers, function(item) {
                return item._links.self.href === user._links.self.href;
            })) {
                return;
            }

            $scope.createdUsers.unshift(user);
        };

        function getCriteria() {
            var params = $location.search(),
                criteria = {
                    max_results: $scope.maxResults
                };

            if (params.q) {
                criteria.where = JSON.stringify({
                    '$or': [
                        {username: {'$regex': params.q, '$options': '-i'}},
                        {first_name: {'$regex': params.q, '$options': '-i'}},
                        {last_name: {'$regex': params.q, '$options': '-i'}},
                        {email: {'$regex': params.q, '$options': '-i'}}
                    ]
                });
            }

            if (params.page) {
                criteria.page = parseInt(params.page, 10);
            }

            if (params.sort) {
                criteria.sort = formatSort(params.sort[0], params.sort[1]);
            } else {
                criteria.sort = formatSort('full_name', 'asc');
            }

            return criteria;
        }

        function fetchUsers(criteria) {
            api.users.query(criteria)
                .then(function(users) {
                    $scope.users = users;
                    $scope.createdUsers = [];
                });
        }

        function formatSort(key, dir) {
            var val = dir === 'asc' ? 1 : -1;
            switch (key) {
                case 'full_name':
                    return '[("first_name", ' + val + '), ("last_name", ' + val + ')]';
                default:
                    return '[("' + encodeURIComponent(key) + '", ' + val + ')]';
            }
        }

        $scope.$watch(getCriteria, fetchUsers, true);
    }

    UserEditController.$inject = ['$scope', 'server', 'superdesk', 'user', 'session'];
    function UserEditController($scope, server, superdesk, user, session) {
        $scope.user = user;
        $scope.profile = $scope.user._id === session.identity._id;
    }

    ChangeAvatarController.$inject = ['$scope', 'upload', 'session', 'urls', 'betaService'];
    function ChangeAvatarController($scope, upload, session, urls, beta) {

        $scope.methods = [
            {id: 'upload', label: gettext('Upload from computer')},
            {id: 'camera', label: gettext('Take a picture'), beta: true},
            {id: 'web', label: gettext('Use a Web URL'), beta: true}
        ];

        if (!beta.isBeta()) {
            $scope.methods = _.reject($scope.methods, {beta: true});
        }

        $scope.activate = function(method) {
            $scope.active = method;
            $scope.preview = {};
            $scope.progress = {width: 0};
        };

        $scope.activate($scope.methods[0]);

        $scope.upload = function(config) {
            var form = {};
            form.CropLeft = Math.round(Math.min(config.cords.x, config.cords.x2));
            form.CropRight = Math.round(Math.max(config.cords.x, config.cords.x2));
            form.CropTop = Math.round(Math.min(config.cords.y, config.cords.y2));
            form.CropBottom = Math.round(Math.max(config.cords.y, config.cords.y2));

            if (config.img) {
                form.media = config.img;
            } else if (config.url) {
                form.URL = config.url;
            } else {
                return;
            }

            return urls.resource('upload').then(function(uploadUrl) {
                return upload.start({
                    url: uploadUrl,
                    method: 'POST',
                    data: form
                }).then(function(response) {

                    if (response.data._status === 'ERR'){
                        return;
                    }

                    var picture_url = response.data.renditions.viewImage.href;
                    $scope.locals.data.picture_url = picture_url;
                    $scope.locals.data.avatar = response.data._id;

                    return $scope.resolve(picture_url);
                }, null, function(update) {
                    $scope.progress.width = Math.round(update.loaded / update.total * 100.0);
                });
            });
        };
    }

    /**
     * Delete a user and remove it from list
     */
    UserDeleteCommand.$inject = ['api', 'data', '$q', 'notify', 'gettext'];
    function UserDeleteCommand(api, data, $q, notify, gettext) {
        return api.users.remove(data.item).then(function(response) {
            data.list.splice(data.index, 1);
        }, function(response) {
            notify.error(gettext('I\'m sorry but can\'t delete the user right now.'));
        });
    }

    /**
     * Resolve a user by route id and redirect to /users if such user does not exist
     */
    UserResolver.$inject = ['api', '$route', 'notify', 'gettext', '$location'];
    function UserResolver(api, $route, notify, gettext, $location) {
        return api.users.getById($route.current.params._id)
            .then(null, function(response) {
                if (response.status === 404) {
                    $location.path('/users/');
                    notify.error(gettext('User was not found, sorry.'), 5000);
                }

                return response;
            });
    }

    return angular.module('superdesk.users', [
        'superdesk.activity',
        'superdesk.users.profile',
        'superdesk.users.activity'
    ])

        .service('users', UsersService)
        .factory('userList', UserListService)

        .factory('rolesLoader', ['$q', 'em', function ($q, em) {
            var delay = $q.defer();

            function zip(items, key) {
                var zipped = {};
                _.each(items, function(item) {
                    zipped[item[key]] = item;
                });

                return zipped;
            }

            em.repository('user_roles').all().then(function(data) {
                var roles = zip(data._items, '_id');
                delay.resolve(roles);
            });

            return delay.promise;
        }])

        .factory('userPopup', ['$compile', '$timeout', 'userList', function ($compile, $timeout, userList) {
            var popover = {};
            var holdInterval = 300;

            // Create element
            popover.get = function(create) {
                if (!popover.element && create) {
                    popover.element = $('<div class="user-popup"></div>');
                    popover.element.appendTo('BODY');
                    popover.element.hover(preventClose, triggerClose);
                    popover.element.click(hide);
                }
                return popover.element;
            };

            // Set content
            popover.set = function(userId, el, scope) {
                preventClose();
                resetContent();

                // do box positioning
                var box = popover.get(true);
                var position = el.offset();
                box.css({
                    left: position.left + el.outerWidth(),
                    top: position.top + el.outerHeight()
                });

                // get data
                userList.getUser(userId)
                .then(function(user) {
                    buildTemplate(user, scope);
                }, function(response) {
                    console.log(response);
                });

                box.show();
            };

            // Close element
            popover.close = function() {
                var box = popover.get();
                if (!box) {
                    return;
                }
                triggerClose();
            };

            function hide() {
                var box = popover.get();
                if (!box) {
                    return;
                }
                box.hide();
            }

            function resetContent() {
                var box = popover.get();
                if (!box) {
                    return;
                }
                box.html('');
            }
            function preventClose() {
                $timeout.cancel(popover.status);
            }

            function triggerClose() {
                popover.status = $timeout(hide, holdInterval);
            }

            //build template
            function buildTemplate(user, scope) {
                var box = popover.get();
                box.html(
                    '<div class="avatar-holder">' +
                        '<figure class="avatar big">' +
                            '<img sd-user-avatar data-src="user.picture_url">' +
                        '</figure>' +
                    '</div>' +
                    '<div class="title">{{user.display_name}}</div>' +
                    '<div class="actions">' +
                        '<a href="#/users/{{user._id}}">go to profile</a>' +
                    '</div>'
                );
                var popupScope = scope.$new(true);
                popupScope.user = user;
                $compile(box)(popupScope);
            }

            return popover;
        }])

        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .permission('users-manage', {
                    label: gettext('Manage users'),
                    permissions: {users: {write: true}}
                })
                .permission('users-read', {
                    label: gettext('Read users'),
                    permissions: {users: {read: true}}
                })
                .permission('user-roles-manage', {
                    label: gettext('Manage user roles'),
                    permissions: {'user_roles': {write: true}}
                })
                .permission('user-roles-read', {
                    label: gettext('Read user roles'),
                    permissions: {'user_roles': {read: true}}
                });
        }])

        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/users/', {
                    label: gettext('Users'),
                    priority: 100,
                    controller: UserListController,
                    templateUrl: 'scripts/superdesk-users/views/list.html',
                    category: superdesk.MENU_MAIN,
                    reloadOnSearch: false,
                    filters: [
                        {
                            action: superdesk.ACTION_PREVIEW,
                            type: 'user'
                        },
                        {action: 'list', type: 'user'}
                    ]
                })
                .activity('/users/:_id', {
                    label: gettext('Users profile'),
                    priority: 100,
                    controller: UserEditController,
                    templateUrl: 'scripts/superdesk-users/views/edit.html',
                    resolve: {user: UserResolver},
                    filters: [{action: 'detail', type: 'user'}]
                })
                .activity('/profile/', {
                    label: gettext('My Profile'),
                    controller: UserEditController,
                    templateUrl: 'scripts/superdesk-users/views/edit.html',
                    resolve: {
                        user: ['session', 'api', function(session, api) {
                            return api.users.getByUrl(session.identity._links.self.href);
                        }]
                    }
                })

                /*
                .activity('/settings/user-roles', {
                    label: gettext('User Roles'),
                    templateUrl: require.toUrl('./views/settings.html'),
                    controller: require('./controllers/settings'),
                    category: superdesk.MENU_SETTINGS,
                    priority: -500
                })
                */

                .activity('delete/user', {
                    label: gettext('Delete user'),
                    icon: 'trash',
                    confirm: gettext('Please confirm you want to delete a user.'),
                    controller: UserDeleteCommand,
                    filters: [
                        {
                            action: superdesk.ACTION_EDIT,
                            type: 'user'
                        }
                    ]
                })
                .activity('edit.avatar', {
                    label: gettext('Change avatar'),
                    modal: true,
                    cssClass: 'upload-avatar',
                    controller: ChangeAvatarController,
                    templateUrl: 'scripts/superdesk-users/views/change-avatar.html',
                    filters: [{action: 'edit', type: 'avatar'}]
                });
        }])

        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('users', {
                type: 'http',
                backend: {rel: 'users'}
            });
        }])

        .config(['$compileProvider', function($compileProvider) {
            // configure new 'compile' directive by passing a directive
            // factory function. The factory function injects the '$compile'
            $compileProvider.directive('compile', ['$compile', function($compile) {
              // directive factory creates a link function
              return function(scope, element, attrs) {
                var value = scope.$eval(attrs.compile);
                element.html(value);
                var nscope = scope.$new(true);
                _.each(scope.$eval(attrs.data), function(value, key) {
                    nscope[key] = value;
                });
                $compile(element.contents())(nscope);
              };
            }]);
        }])

        .directive('sdInfoItem', function() {
            return {
                link: function (scope, element) {
                    element.addClass('item');
                    element.find('input').addClass('info-value');
                    element.find('input').addClass('info-editable');
                }
            };
        })

        .directive('sdValidError', function() {
            return {
                link: function (scope, element) {
                    element.addClass('validation-error');
                }
            };
        })

        .directive('sdValidInfo', function() {
            return {
                link: function (scope, element) {
                    element.addClass('validation-info');
                }
            };
        })

        .directive('sdRolesTreeview', ['$compile', function($compile) {
            return {
                restrict: 'A',
                terminal: true,
                scope: {role: '=', roles: '='},
                link: function(scope, element, attrs) {

                    if (scope.role['extends'] !== undefined) {
                        scope.childrole = scope.roles[_.findKey(scope.roles, {_id: scope.role['extends']})];
                        scope.treeTemplate = 'scripts/superdesk-users/views/rolesTree.html';
                    } else {
                        scope.treeTemplate = 'scripts/superdesk-users/views/rolesLeaf.html';
                    }

                    var template = '<div class="role-holder" ng-include="treeTemplate"></div>';

                    var newElement = angular.element(template);
                    $compile(newElement)(scope);
                    element.replaceWith(newElement);
                }
            };
        }])

        .directive('sdUserActivity', ['profileService', function(profileService) {
            return {
                restrict: 'A',
                replace: true,
                templateUrl: 'scripts/superdesk-users/views/activity-feed.html',
                scope: {
                    user: '='
                },
                link: function(scope, element, attrs) {
                    var page = 1;
                    var maxResults = 5;

                    scope.$watch('user', function() {
                        profileService.getUserActivity(scope.user, maxResults).then(function(list) {
                            scope.activityFeed = list;
                        });
                    });

                    scope.loadMore = function() {
                        page++;
                        profileService.getUserActivity(scope.user, maxResults, page).then(function(next) {
                            Array.prototype.push.apply(scope.activityFeed._items, next._items);
                            scope.activityFeed._links = next._links;
                        });
                    };
                }
            };
        }])

        .directive('sdUserDetailsPane', ['$timeout', function($timeout) {
            return {
                replace: true,
                transclude: true,
                template: '<div class="user-details-pane" ng-transclude></div>',
                link: function(scope, element, attrs) {
                    $timeout(function() {
                        $('.user-details-pane').addClass('open');
                    });

                    scope.closePane = function() {
                        $('.user-details-pane').removeClass('open');
                    };
                }
            };
        }])

        .directive('sdUserEdit', ['gettext', 'notify', 'users', 'session', '$location', '$route', 'superdesk',
        function(gettext, notify, users, session, $location, $route, superdesk) {

            return {
                templateUrl: 'scripts/superdesk-users/views/edit-form.html',
                scope: {
                    origUser: '=user',
                    onsave: '&',
                    oncancel: '&'
                },
                link: function(scope, elem) {

                    scope.usernamePattern = users.usernamePattern;
                    scope.phonePattern = users.phonePattern;
                    scope.dirty = false;

                    scope.$watch('origUser', resetUser);

                    scope.$watchCollection('user', function(user) {
                        _.each(user, function(value, key) {
                            if (value === '') {
                                delete user[key];
                            }
                        });
                        scope.dirty = !angular.equals(user, scope.origUser);
                    });

                    scope.cancel = function() {
                        resetUser(scope.origUser);
                        if (!scope.origUser.Id) {
                            scope.oncancel();
                        }
                    };

                    scope.editPicture = function() {
                        superdesk.intent('edit', 'avatar', scope.user).then(function(avatar) {
                            scope.user.picture_url = avatar; // prevent replacing Avatar which would get into diff
                        });
                    };

                    scope.save = function() {
                        scope.error = null;
                        notify.info(gettext('saving..'));
                        return users.save(scope.origUser, scope.user).then(function() {
                            resetUser(scope.origUser);
                            notify.pop();
                            notify.success(gettext('user saved.'));
                            scope.onsave({user: scope.origUser});

                            if (scope.user._id === session.identity._id) {
                                session.updateIdentity(scope.user);
                            }

                        }, function(response) {
                            notify.pop();
                            if (response.status === 404) {
                                if ($location.path() === '/users/') {
                                    $route.reload();
                                } else {
                                    $location.path('/users/');
                                }
                                notify.error(gettext('User is not found. It might be deleted.'));
                            } else {
                                if (response.data && response.data._issues) {
                                    scope.error = response.data._issues;
                                    for (var field in response.data._issues) {
                                        if (scope.userForm[field]) {
                                            for (var constraint in response.data._issues[field]) {
                                                if (response.data._issues[field][constraint]) {
                                                    scope.userForm[field].$setValidity(constraint, false);
                                                }
                                            }
                                        }
                                    }
                                }
                                notify.error(gettext('Hmm, there was an error when saving user. '));
                            }
                        });
                    };

                    scope.toggleStatus = function(active) {
                        users.toggleStatus(scope.origUser, active).then(function() {
                            resetUser(scope.origUser);
                        });
                    };

                    function resetUser(user) {
                        scope.error = null;
                        scope.user = _.create(user);
                        scope.confirm = {password: null};
                        scope.show = {password: false};
                        scope._active = users.isActive(user);
                    }
                }
            };
        }])

        .directive('sdUserPreferences', ['api', 'session', function(api, session) {
            return {
                templateUrl: 'scripts/superdesk-users/views/user-preferences.html',
                link: function(scope, elem, attrs) {

                    var orig;

                    

                    api('preferences').getById(session.sessionId)
                    .then(function(result) {
                        orig = result;
                        buildPreferences(orig);
                    });

                    scope.cancel = function() {
                        scope.userPrefs.$setPristine();
                        buildPreferences(orig);
                    };

                    scope.save = function() {
                        api('preferences', session.sessionId)
                        .save(orig, patch())
                        .then(function(result) {
                            scope.cancel();
                        }, function(response) {
                            console.log(response);
                        });
                    };

                    function buildPreferences(struct) {
                        scope.preferences = {};
                        _.each(struct.preferences, function(val, key) {
                            scope.preferences[key] = _.create(val);
                        });
                    }

                    function patch() {
                        var p = {preferences: {}};
                        _.each(orig.preferences, function(val, key) {
                            p.preferences[key] = _.extend(val, scope.preferences[key]);
                        });
                        return p;
                    }
                }
            };
        }])

        .directive('sdChangePassword', ['api', 'notify', 'gettext', function(api, notify, gettext) {
            return {
                link: function(scope, element) {
                    scope.$watch('user', function() {
                        scope.oldPasswordInvalid = false;
                    });

                    /**
                     * change user password
                     *
                     * @param {string} oldPassword
                     * @param {string} newPassword
                     */
                    scope.changePassword = function(oldPassword, newPassword) {
                        return api.users.changePassword(scope.user, oldPassword, newPassword)
                            .then(function(response) {
                                scope.oldPasswordInvalid = false;
                                notify.success(gettext('New password is saved now.'), 3000);
                                scope.show.password = false;
                            }, function(response) {
                                scope.oldPasswordInvalid = true;
                            });
                    };
                }
            };
        }])

        .directive('sdUserUnique', ['$q', 'api', function($q, api) {
            return {
                require: 'ngModel',
                scope: {exclude: '='},
                link: function (scope, element, attrs, ctrl) {

                    /**
                     * Test if given value is unique for seleted field
                     */
                    function testUnique(modelValue, viewValue) {
                        var value = modelValue || viewValue;
                        if (value && attrs.uniqueField) {
                            var criteria = {where: {}};
                            criteria.where[attrs.uniqueField] = value;
                            return api.users.query(criteria)
                                .then(function(users) {

                                    if (users._items.length && (!scope.exclude._id || users._items[0]._id !== scope.exclude._id)) {
                                        return $q.reject(users);
                                    }

                                    return users;
                                });
                        }

                        // mark as ok
                        return $q.when();
                    }

                    ctrl.$asyncValidators.unique = testUnique;
                }
            };
        }])

        .directive('sdPasswordConfirm', [function() {
            var NAME = 'confirm';
            return {
                require: 'ngModel',
                scope: {password: '='},
                link: function (scope, element, attrs, ctrl) {

                    function isMatch(password, confirm) {
                        return !password || password === confirm;
                    }

                    ctrl.$validators[NAME] = function(modelValue, viewValue) {
                        var value = modelValue || viewValue;
                        return isMatch(scope.password, value);
                    };

                    scope.$watch('password', function(password) {
                        ctrl.$setValidity(NAME, isMatch(password, ctrl.$viewValue));
                    });
                }
            };
        }])

        .directive('sdUserList', ['keyboardManager', function(keyboardManager) {
            return {
                templateUrl: 'scripts/superdesk-users/views/user-list-item.html',
                scope: {
                    users: '=',
                    selected: '=',
                    done: '='
                },
                link: function(scope, elem, attrs) {
                    scope.select = function(user) {
                        scope.selected = user;
                    };

                    scope.$watch('users', function(users) {
                    });

                    function getSelectedIndex() {
                        return _.findIndex(scope.users, scope.selected);
                    }

                    keyboardManager.bind('up', function() {
                        var selectedIndex = getSelectedIndex();
                        if (selectedIndex !== -1) {
                            scope.select(scope.users[_.max([0, selectedIndex - 1])]);
                        }
                    });

                    keyboardManager.bind('down', function() {
                        var selectedIndex = getSelectedIndex();
                        if (selectedIndex !== -1) {
                            scope.select(scope.users[_.min([scope.users.length - 1, selectedIndex + 1])]);
                        }
                    });
                }
            };
        }])

        .directive('sdUserListItem', function() {
            return {
                templateUrl: 'scripts/superdesk-users/views/user-list-item.html'
            };
        })

        .directive('sdActivity', function() {
            return {
                templateUrl: 'scripts/superdesk-users/views/activity-list.html'
            };
        })

        .directive('sdUserMentio', ['mentioUtil', 'api', 'userList', function(mentioUtil, api, userList) {
            return {
                templateUrl: 'scripts/superdesk-users/views/mentions.html',
                link: function(scope, elem) {
                    scope.users = [];

                    // filter user by given prefix
                    scope.searchUsers = function(prefix) {

                        return userList.get(prefix, 1, 10)
                        .then(function(result) {
                            scope.users = _.sortBy(result._items, 'username');
                        });

                    };

                    scope.selectUser = function(user) {
                        return '@' + user.username;
                    };
                }
            };
        }])

        .directive('sdUserInfo', ['userPopup', function(userPopup) {
            return {
                link: function(scope, element, attrs) {
                    element.addClass('user-link');
                    element.hover(function() {
                        userPopup.set(attrs.user, element, scope);
                    }, function() {
                        userPopup.close();
                    });
                }
            };
        }])

        ;

})();
