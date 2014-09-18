define([
    'lodash',
    'jquery',
    'angular',
    'require'
], function(_, $, angular, require) {
    'use strict';

    angular.module('superdesk.users.directives', [])
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
        .directive('sdUserEdit', ['gettext', 'notify', 'api', 'session', '$location', '$route', 'superdesk',
        function(gettext, notify, api, session, $location, $route, superdesk) {

            var USERNAME_REGEXP = /^[A-Za-z0-9_.'-]+$/;
            var PHONE_REGEXP = /^(?:(?:0?[1-9][0-9]{8})|(?:(?:\+|00)[1-9][0-9]{9,11}))$/;

            return {
                replace: true,
                templateUrl: require.toUrl('./views/edit-form.html'),
                scope: {
                    origUser: '=user',
                    onsave: '&',
                    oncancel: '&'
                },
                link: function(scope, elem) {

                    scope.usernamePattern = USERNAME_REGEXP;
                    scope.phonePattern = PHONE_REGEXP;
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
                        return api.users.save(scope.origUser, scope.user).then(function(response) {
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

                    function resetUser(user) {
                        scope.error = null;
                        scope.user = _.create(user);
                        scope.confirm = {password: null};
                        scope.show = {password: false};
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
                templateUrl: 'scripts/superdesk-users/views/user-list-item.html',
                scope: {
                    user: '=',
                    list: '=',
                    index: '='
                }
            };
        })

        .directive('sdActivity', function() {
            return {
                templateUrl: 'scripts/superdesk-users/views/activity-list.html'
            };
        })
        .directive('sdUserMentio', ['mentioUtil', '$q', 'userList', function(mentioUtil, $q, userList) {
            return {
                templateUrl: 'scripts/superdesk-users/views/mentions.html',
                link: function(scope, elem) {
                    scope.searchUsers = function(term) {
                        var userlist = [];
                        userList.get()
                        .then(function(result) {
                            _.each(result._items, function(item) {
                                if (item.display_name.toUpperCase().indexOf(term.toUpperCase()) >= 0) {
                                    userlist.push(item);
                                }
                            });
                            scope.users = userlist;
                            return $q.when(userlist);
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
        }]);
});
