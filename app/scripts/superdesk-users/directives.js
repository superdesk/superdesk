define([
    'lodash',
    'jquery',
    'angular'
], function(_, $, angular) {
    'use strict';

    angular.module('superdesk.users.directives', [])

        .directive('sdInfoItem', function() {
            return {
                link: function (scope, element) {
                    element.addClass('info-item');
                    element.find('label').addClass('info-label');
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
        .directive('sdTriggerSearch', function() {
            return {
                link: function (scope, element) {
                    element.find('.trigger-icon').click(function(e) {
                        element.toggleClass('open');
                        if (element.hasClass('open')) {
                            element.find('input').focus();
                        }
                    });
                }
            };
        })
        .directive('sdSearchParam', ['$location', function($location) {
            return {
                scope: {
                    sdSearchParam: '@'
                },
                link: function(scope, elem) {
                    var params = $location.search();
                    elem.val(params[scope.sdSearchParam]);

                    var updateParam = _.debounce(function() {
                        scope.$apply(function() {
                            $location.search('q', elem.val() || null);
                            $location.search('page', null);
                        });
                    }, 500);

                    elem.keyup(updateParam);
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
        .directive('sdUserEdit', ['gettext', 'notify', 'api', function(gettext, notify, api) {

            var USERNAME_REGEXP = /^[A-Za-z0-9_.'-]+$/;
            var PHONE_REGEXP = /^(?:(?:0?[1-9][0-9]{8})|(?:(?:\+|00)[1-9][0-9]{9,11}))$/;

            return {
                replace: true,
                templateUrl: 'scripts/superdesk-users/views/edit-form.html',
                scope: {
                    origUser: '=user',
                    onsave: '&'
                },
                link: function(scope, elem) {

                    scope.usernamePattern = USERNAME_REGEXP;
                    scope.phonePattern = PHONE_REGEXP;

                    scope.$watch('origUser', function(user) {
                        scope.reset(user);
                    });

                    scope.reset = function(user) {
                        scope.error = null;
                        scope.user = angular.copy(user);
                        scope.confirm = {password: null};
                        scope.show = {password: false};
                    };

                    /**
                     * save user
                     */
                    scope.save = function() {
                        scope.error = null;
                        notify.info(gettext('saving..'));
                        return api.users.save(scope.origUser, scope.user).then(function() {
                            notify.pop();
                            notify.success(gettext('user saved.'), 3000);
                            scope.onsave({user: scope.origUser});
                        }, function(response) {
                            notify.pop();
                            if (response.status === 400) {
                                scope.error = response.data;
                            } else if (response.status === 404) {
                                scope.origUser = null;
                                console.error(response);
                                notify.error(gettext('User is not found. It might be deleted.'));
                            } else {
                                console.error(response);
                                notify.error(gettext('Hmm, there was an error when saving user.'));
                            }
                        });
                    };
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
        .directive('sdUserPicture', function() {
            var PICTURE_DEFAULT = 'https://avatars.githubusercontent.com/u/275305';
            return {
                scope: {src: '='},
                link: function (scope, element, attrs) {

                    scope.$watch('src', function(src) {
                        src = src || PICTURE_DEFAULT;
                        element.attr('src', src);
                    });

                    element.on('error', function (e) {
                        console.log(e);
                        return;
                    });
                }
            };
        })
        .directive('sdUserUnique', ['resource', function(resource) {
            var NAME = 'unique';
            return {
                require: 'ngModel',
                scope: {exclude: '='},
                link: function (scope, element, attrs, ctrl) {

                    /**
                     * Test if given value is unique for seleted field
                     *
                     * @param {string} viewValue
                     * @returns {string}
                     */
                    function testUnique(viewValue) {
                        if (viewValue && attrs.uniqueField) {
                            var criteria = {};
                            criteria[attrs.uniqueField] = viewValue;
                            resource.users.query(criteria)
                                .then(function(users) {
                                    if (scope.exclude && users.total === 1) {
                                        ctrl.$setValidity(NAME, users._items[0].Id === scope.exclude.Id);
                                    } else {
                                        ctrl.$setValidity(NAME, !users.total);
                                    }
                                });
                        }

                        return reset(viewValue);
                    }

                    function reset(value) {
                        ctrl.$setValidity(NAME, true);
                        return value;
                    }

                    ctrl.$parsers.push(testUnique);
                    ctrl.$formatters.push(reset);
                }
            };
        }])
        .directive('sdPasswordConfirm', [function() {
            var NAME = 'confirm';
            return {
                require: 'ngModel',
                scope: {password: '='},
                link: function (scope, element, attrs, ctrl) {
                    function testPassword(viewValue) {
                        if (viewValue && scope.password) {
                            ctrl.$setValidity(NAME, viewValue === scope.password);
                        }

                        return viewValue;
                    }

                    function reset(value) {
                        ctrl.$setValidity(NAME, true);
                        return value;
                    }

                    ctrl.$parsers.push(testPassword);
                    ctrl.$formatters.push(reset);
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
        });
});
