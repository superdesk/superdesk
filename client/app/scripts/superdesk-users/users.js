(function() {
    'use strict';

    /**
     * Bussiness logic layer, should be used instead of resource
     */
    UsersService.$inject = ['api', '$q', 'notify'];
    function UsersService(api, $q, notify) {

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
                }, function(response) {
                    if (angular.isDefined(response.data._issues) &&
                            angular.isDefined(response.data._issues['validator exception'])) {
                        notify.error(gettext('Error: ' + response.data._issues['validator exception']));
                    } else {
                        notify.error(gettext('Error. User Profile not updated.'));
                    }
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
        this.changePassword = function changePassword(user, oldPassword, newPassword) {
            return api.changePassword.create({username: user.username, old_password: oldPassword, new_password: newPassword})
            	.then(function(result) {});
        };

        /**
         * Reset reset password
         *
         * @param {Object} user
         * @returns {Promise}
         */
        this.resetPassword = function resetPassword(user) {
            return api.resetPassword.create({email: user.email})
                .then(function(result) {});
        };

        /**
         * Test if user is active
         */
        this.isActive = function isActive(user) {
            return user && user.is_active;
        };

        /**
         * Test if user is on pending state
         */
        this.isPending = function isPending(user) {
            return user && user.needs_activation;
        };

        /**
         * Toggle user status
         */
        this.toggleStatus = function toggleStatus(user, active) {
            return this.save(user, {is_active: active});
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
            return api('users').getById(id, undefined, true);
        };

        /**
         * Clear user cache
         */
        userservice.clearCache = function() {
        	cache.removeAll();
        };

        function buildKey(key, page, perPage) {
            return key + '_' + page + '_' + perPage;
        }

        return userservice;
    }

    UserListController.$inject = ['$scope', '$location', 'api'];
    function UserListController($scope, $location, api) {
        var DEFAULT_SIZE = 25;

        $scope.selected = {user: null};
        $scope.createdUsers = [];

        api('roles').query().then(function(result) {
            $scope.roles = _.indexBy(result._items, '_id');
            $scope.noRolesWarning = result._items.length === 0;
        });

        $scope.preview = function(user) {
            $scope.selected.user = user;
        };

        $scope.createUser = function() {
            $scope.intent('create', 'user').then(fetchUsers);
        };

        $scope.$on('intent:create:user', function createUser() {
            // fallback if there is no other activity
            $scope.preview({});
        });

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
            if (!findUser($scope.users._items, user) && !findUser($scope.createdUsers, user)) {
                $scope.createdUsers.unshift(user);
            }
        };

        function findUser(list, user) {
            return _.find(list, function(item) {
                return item._links.self.href === user._links.self.href;
            });
        }

        function getCriteria() {
            var params = $location.search(),
                criteria = {
                    max_results: Number(params.max_results) || DEFAULT_SIZE
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

        beta.isBeta().then(function(beta) {
            if (!beta) {
                $scope.methods = _.reject($scope.methods, {beta: true});
            }
        });

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
     * Enable user
     */
    UserEnableCommand.$inject = ['api', 'data', '$q', 'notify', 'gettext', 'users', '$rootScope'];
    function UserEnableCommand(api, data, $q, notify, gettext, users, $rootScope) {
    	var user = data.item;

        return users.save(user, {'is_enabled': true, 'is_active': true}).then(
            function(response) {
                $rootScope.$broadcast('user:updated', response);
            },
            function(response) {
                if (angular.isDefined(response.data._issues) &&
                    angular.isDefined(response.data._issues['validator exception'])) {
                    notify.error(gettext('Error: ' + response.data._issues['validator exception']));
                } else if (angular.isDefined(response.data._message)) {
                    notify.error(gettext('Error: ' + response.data._message));
                } else {
                    notify.error(gettext('Error. User Profile cannot be enabled.'));
                }
            }
        );
    }

    /**
     * Disable user
     */
    UserDeleteCommand.$inject = ['api', 'data', '$q', 'notify', 'gettext', '$rootScope'];
    function UserDeleteCommand(api, data, $q, notify, gettext, $rootScope) {
    	var user = data.item;
        return api.users.remove(user).then(
            function(response) {
                return api.users.getById(user._id)
                .then(function(newUser) {
                    user = angular.extend(user, newUser);
                    $rootScope.$broadcast('user:updated', user);
                    return user;
                });
            },
            function(response) {
                if (angular.isDefined(response.data._issues) &&
                    angular.isDefined(response.data._issues['validator exception'])) {
                    notify.error(gettext('Error: ' + response.data._issues['validator exception']));
                } else if (angular.isDefined(response.data._message)) {
                    notify.error(gettext('Error: ' + response.data._message));
                } else {
                    notify.error(gettext('Error. User Profile cannot be disabled.'));
                }
            }
        );
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

    UserRolesDirective.$inject = ['api', 'gettext', 'notify', 'modal'];
    function UserRolesDirective(api, gettext, notify, modal) {
        return {
            scope: true,
            templateUrl: 'scripts/superdesk-users/views/settings-roles.html',
            link: function(scope) {
                var _orig = null;
                scope.editRole = null;

                api('roles').query()
                .then(function(result) {
                    scope.roles = result._items;
                });

                scope.edit = function(role) {
                    scope.editRole = _.create(role);
                    _orig = role;
                    scope.defaultRole = role.is_default;
                };

                scope.save = function(role) {
                    var _new = role._id ? false : true;
                    api('roles').save(_orig, role)
                    .then(function() {
                        if (_new) {
                            scope.roles.push(_orig);
                            notify.success(gettext('User role created.'));
                        } else {
                            notify.success(gettext('User role updated.'));
                        }
                        if (role.is_default) {
                            updatePreviousDefault(role);
                        }
                        scope.cancel();
                    }, function(response) {
                        if (response.status === 400 && typeof(response.data._issues.name) !== 'undefined' &&
                        response.data._issues.name.unique === 1) {
                            notify.error(gettext('I\'m sorry but a role with that name already exists.'));
                        } else {
                            if (typeof(response.data._issues['validator exception']) !== 'undefined') {
                                    notify.error(response.data._issues['validator exception']);
                                } else {
                                notify.error(gettext('I\'m sorry but there was an error when saving the role.'));
                            }
                        }
                    });
                };

                scope.cancel = function() {
                    scope.editRole = null;
                };

                scope.remove = function(role) {
                    confirm().then(function() {
                        api('roles').remove(role)
                        .then(function(result) {
                            _.remove(scope.roles, role);
                        }, function(response) {
                            if (angular.isDefined(response.data._message)) {
                                notify.error(gettext('Error: ' + response.data._message));
                            } else {
                                notify.error(gettext('There is an error. Role cannot be deleted.'));
                            }
                        });
                    });
                };

                function updatePreviousDefault(role) {

                    //find previous role with flag 'default'
                    var previous = _.find(scope.roles, function(r) {
                      return r._id !== role._id && r.is_default;
                    });

                    // update it
                    if (previous) {
                        api('roles').getById(previous._id).then(function(result) {
                            _.extend(previous, {_etag: result._etag, is_default: false});
                        });
                    }
                }

                function confirm() {
                    return modal.confirm(gettext('Are you sure you want to delete user role?'));
                }
            }
        };
    }

    RolesPrivilegesDirective.$inject = ['api', 'gettext', 'notify', '$q'];
    function RolesPrivilegesDirective(api, gettext, notify, $q) {
        return {
            scope: true,
            templateUrl: 'scripts/superdesk-users/views/settings-privileges.html',
            link: function(scope) {

                api('roles').query()
                .then(function(result) {
                    scope.roles = result._items;
                });

                api('privileges').query().
                then(function(result) {
                    scope.privileges = result._items;
                });

                scope.saveAll = function(rolesForm) {
                    var promises = [];

                    _.each(scope.roles, function(role) {
                        promises.push(api.save('roles', role, _.pick(role, 'privileges'))
                        .then(function(result) {
                        }, function(error) {
                            console.log(error);
                        }));
                    });

                    $q.all(promises).then(function() {
                        notify.success(gettext('Privileges updated.'));
                        rolesForm.$setPristine();
                    }, function() {
                        notify.success(gettext('Error. Privileges not updated.'));
                    });
                };
            }
        };
    }
    /**
     * User roles controller - settings page
     */
    UserRolesController.$inject = ['$scope'];
    function UserRolesController($scope) {
    }

    return angular.module('superdesk.users', [
        'superdesk.activity',
        'superdesk.asset'
    ])

        .controller('UserEditController', UserEditController) // make it available to user.profile
        .service('users', UsersService)
        .factory('userList', UserListService)

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
                popover.status = $timeout(hide, holdInterval, false);
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

        .config(['superdeskProvider', 'assetProvider', function(superdesk, asset) {
            superdesk
                .activity('/users/', {
                    label: gettext('Users'),
                    description: gettext('Find your colleagues'),
                    priority: 100,
                    controller: UserListController,
                    templateUrl: asset.templateUrl('superdesk-users/views/list.html'),
                    category: superdesk.MENU_MAIN,
                    reloadOnSearch: false,
                    filters: [
                        {
                            action: superdesk.ACTION_PREVIEW,
                            type: 'user'
                        },
                        {action: 'list', type: 'user'}
                    ],
                    privileges: {users: 1}
                })
                .activity('/users/:_id', {
                    label: gettext('Users profile'),
                    priority: 100,
                    controller: 'UserEditController',
                    templateUrl: asset.templateUrl('superdesk-users/views/edit.html'),
                    resolve: {user: UserResolver},
                    filters: [{action: 'detail', type: 'user'}],
                    privileges: {users: 1}
                })
                .activity('/settings/user-roles', {
                    label: gettext('User Roles'),
                    templateUrl: asset.templateUrl('superdesk-users/views/settings.html'),
                    controller: UserRolesController,
                    category: superdesk.MENU_SETTINGS,
                    priority: -500,
                    privileges: {roles: 1}
                })
                .activity('delete/user', {
                    label: gettext('Disable user'),
                    icon: 'trash',
                    confirm: gettext('Please confirm that you want to disable a user.'),
                    controller: UserDeleteCommand,
                    filters: [
                        {
                            action: superdesk.ACTION_EDIT,
                            type: 'user'
                        }
                    ],
                    condition: function(data) {
                        return data.is_enabled;
                    },
                    privileges: {users: 1}
                })
                .activity('restore/user', {
                    label: gettext('Enable user'),
                    icon: 'revert',
                    controller: UserEnableCommand,
                    filters: [
                        {
                            action: superdesk.ACTION_EDIT,
                            type: 'user'
                        }
                    ],
                    condition: function(data) {
                        return !data.is_enabled;
                    },
                    privileges: {users: 1}
                })
                .activity('edit.avatar', {
                    label: gettext('Change avatar'),
                    modal: true,
                    cssClass: 'upload-avatar',
                    controller: ChangeAvatarController,
                    templateUrl: asset.templateUrl('superdesk-users/views/change-avatar.html'),
                    filters: [{action: 'edit', type: 'avatar'}]
                });
        }])

        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('users', {
                type: 'http',
                backend: {rel: 'users'}
            });
            apiProvider.api('roles', {
                type: 'http',
                backend: {rel: 'roles'}
            });
            apiProvider.api('resetPassword', {
                type: 'http',
                backend: {rel: 'reset_user_password'}
            });
            apiProvider.api('changePassword', {
                type: 'http',
                backend: {rel: 'change_user_password'}
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

        .directive('sdUserRoles', UserRolesDirective)
        .directive('sdRolesPrivileges', RolesPrivilegesDirective)

        .directive('sdInfoItem', function() {
            return {
                link: function (scope, element) {
                    element.addClass('item');
                    element.find('input, select')
                        .addClass('info-value info-editable');
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

        .directive('sdUserDetailsPane', ['$timeout', function($timeout) {
            return {
                replace: true,
                transclude: true,
                template: '<div class="user-details-pane" ng-transclude></div>',
                link: function(scope, element, attrs) {
                    $timeout(function() {
                        $('.user-details-pane').addClass('open');
                    }, 0, false);

                    scope.closePane = function() {
                        $('.user-details-pane').removeClass('open');
                    };
                }
            };
        }])

        .directive('sdUserEdit', ['api', 'gettext', 'notify', 'users', 'userList', 'session',
            '$location', '$route', 'superdesk', 'features', 'asset', 'privileges', 'desks', 'keyboardManager',
        function(api, gettext, notify, users, userList, session, $location, $route, superdesk, features,
                 asset, privileges, desks, keyboardManager) {

            return {
                templateUrl: asset.templateUrl('superdesk-users/views/edit-form.html'),
                scope: {
                    origUser: '=user',
                    onsave: '&',
                    oncancel: '&',
                    onupdate: '&'
                },
                link: function(scope, elem) {
                    scope.privileges = privileges.privileges;
                    scope.features = features;
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

                    api('roles').query().then(function(result) {
                        scope.roles = result._items;
                    });

                    scope.cancel = function() {
                        resetUser(scope.origUser);
                        if (!scope.origUser.Id) {
                            scope.oncancel();
                        }
                    };
                    scope.focused = function() {
                        keyboardManager.unbind('down');
                        keyboardManager.unbind('up');
                    };

                    scope.editPicture = function() {
                        superdesk.intent('edit', 'avatar', scope.user).then(function(avatar) {
                            scope.user.picture_url = avatar; // prevent replacing Avatar which would get into diff
                        });
                    };
                    scope.save = function() {
                        scope.error = null;
                        notify.info(gettext('saving..'));

                        return users.save(scope.origUser, scope.user)
                        .then(function(response) {
                            scope.origUser = response;
                            resetUser(scope.origUser);
                            notify.pop();
                            notify.success(gettext('user saved.'));
                            scope.onsave({user: scope.origUser});

                            if (scope.user._id === session.identity._id) {
                                session.updateIdentity(scope.origUser);
                            }

                            userList.clearCache();

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
                                            if (scope.error[field]) {
                                                scope.error[field].format = true;
                                            }
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
                            scope.onupdate({user: scope.origUser});
                        });
                    };

                    function resetUser(user) {
                        scope.error = null;
                        scope.user = _.create(user);
                        scope.confirm = {password: null};
                        scope.show = {password: false};
                        scope._active = users.isActive(user);
                        scope._pending = users.isPending(user);
                        scope.profile = scope.user._id === session.identity._id;

                        if (angular.isDefined(user) && angular.isDefined(user._links)) {
                            desks.fetchUserDesks(user).then(function(response) {
                                scope.userDesks = response._items;
                            });
                        }
                    }

                    scope.$on('user:updated', function(event, user) {
                        resetUser(user);
                    });
                }
            };
        }])
        .directive('sdUserPreferences', ['api', 'session', 'preferencesService', 'notify', 'asset',
            function(api, session, preferencesService, notify, asset) {
            return {
                templateUrl: asset.templateUrl('superdesk-users/views/user-preferences.html'),
                link: function(scope, elem, attrs) {

                    var orig;
                    preferencesService.get().then(function(result) {
                        orig = result;
                        buildPreferences(orig);
                    });

                    scope.cancel = function() {
                        scope.userPrefs.$setPristine();
                        buildPreferences(orig);
                    };

                    scope.save = function() {

                        var update = patch();

                        preferencesService.update(update).then(function() {
                                scope.cancel();
                            }, function(response) {
                                notify.error(gettext('User preferences could not be saved...'));
                        });
                    };

                    function buildPreferences(struct) {
                        scope.preferences = {};
                        _.each(struct, function(val, key) {
                            scope.preferences[key] = _.create(val);
                        });
                    }

                    function patch() {
                        var p = {};
                        _.each(orig, function(val, key) {
                            p[key] = _.extend(val, scope.preferences[key]);
                        });
                        return p;
                    }
                }
            };
        }])
        .directive('sdUserPrivileges', ['api', 'gettext', 'notify', function(api, gettext, notify) {
            return {
                scope: {
                    user: '='
                },
                templateUrl: 'scripts/superdesk-users/views/user-privileges.html',
                link: function(scope) {
                    api('privileges').query().
                    then(function(result) {
                        scope.privileges = result._items;
                    });

                    api('roles').getById(scope.user.role).then(function(role) {
                        scope.role = role;
                    }, function(error) {
                        console.log(error);
                    });

                    scope.save = function(userPrivileges) {
                        api.save('users', scope.user, _.pick(scope.user, 'privileges'))
                        .then(function(result) {
                            notify.success(gettext('Privileges updated.'));
                        }, function(error) {
                            notify.error(gettext('Privileges not updated.'));
                            console.log(error);
                        });
                        userPrivileges.$setPristine();
                    };
                }
            };
        }])
        .directive('sdChangePassword', ['users', 'notify', 'gettext', function(users, notify, gettext) {
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
                        return users.changePassword(scope.user, oldPassword, newPassword)
                            .then(function(response) {
                                scope.oldPasswordInvalid = false;
                                notify.success(gettext('The password has been changed.'), 3000);
                                scope.show.change_password = false;
                            }, function(response) {
                                scope.oldPasswordInvalid = true;
                            });
                    };
                }
            };
        }])

        .directive('sdResetPassword', ['users', 'notify', 'gettext', function(users, notify, gettext) {
            return {
                link: function(scope, element) {
                	scope.$watch('user', function() {
                        scope.oldPasswordInvalid = false;
                    });

                    /**
                     * reset user password
                     */
                    scope.resetPassword = function() {
                        return users.resetPassword(scope.user)
                            .then(function(response) {
                                scope.oldPasswordInvalid = false;
                                notify.success(gettext('The password has been reset.'), 3000);
                                scope.show.reset_password = false;
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

        .directive('sdUserList', ['keyboardManager', 'users', 'asset', function(keyboardManager, users, asset) {
            return {
                templateUrl: asset.templateUrl('superdesk-users/views/user-list-item.html'),
                scope: {
                    roles: '=',
                    users: '=',
                    selected: '=',
                    done: '='
                },
                link: function(scope, elem, attrs) {

                    scope.active = function(user) {
                        return users.isActive(user);
                    };

                    scope.pending = function(user) {
                        return users.isPending(user);
                    };

                    scope.select = function(user) {
                        scope.selected = user;
                        bindKeys();
                    };
                    scope.$watch('selected', function(selected) {
                       if (selected == null) {
                            bindKeys();
                       }
                    });

                    function bindKeys() {
                        unbindKeys();
                        keyboardManager.bind('down', moveDown);
                        keyboardManager.bind('up', moveUp);
                    }

                    function unbindKeys() {
                        keyboardManager.unbind('down');
                        keyboardManager.unbind('up');
                    }

                    function moveDown() {
                        var selectedIndex = getSelectedIndex();
                        if (selectedIndex !== -1) {
                            scope.select(scope.users[_.min([scope.users.length - 1, selectedIndex + 1])]);
                        }
                    }

                    function moveUp() {
                        var selectedIndex = getSelectedIndex();
                        if (selectedIndex !== -1) {
                            scope.select(scope.users[_.max([0, selectedIndex - 1])]);
                        }
                    }

                    function getSelectedIndex() {
                        return _.findIndex(scope.users, scope.selected);
                    }
                }
            };
        }])

        .directive('sdUserListItem', ['asset', function(asset) {
            return {
                templateUrl: asset.templateUrl('superdesk-users/views/user-list-item.html')
            };
        }])

        .directive('sdActivity', ['asset', function(asset) {
            return {
                templateUrl: asset.templateUrl('superdesk-users/views/activity-list.html')
            };
        }])

        .directive('sdUserMentio', ['userList', 'asset', function(userList, asset) {
            return {
                templateUrl: asset.templateUrl('superdesk-users/views/mentions.html'),
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

        .filter('username', ['session', function usernameFilter(session) {
            return function getUsername(user) {
                return user ? user.display_name || user.username : null;
            };
        }])
        ;

})();
