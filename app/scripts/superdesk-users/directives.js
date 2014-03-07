define([
    'lodash',
    'jquery',
    'angular',
    'superdesk/hashlib'
], function(_, $, angular, hashlib) {
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
        .directive('sdUserEdit', ['resource', 'upload', 'gettext', 'notify',
            function(resource, upload, gettext, notify) {
            return {
                replace: true,
                templateUrl: 'scripts/superdesk-users/views/edit-form.html',
                scope: {
                    user: '=',
                    onsave: '&'
                },
                link: function(scope, elem) {
                    scope.editpicture = function() {
                        // todo(petr): well just make it work
                        upload.upload('users').then(function(data) {
                            scope.user.avatar = data.url;
                            resource.users.update(scope.user);
                        });
                    };

                    /**
                     * save user
                     */
                    scope.save = function(user) {

                        // todo(petr): figure out where to put such logic
                        if (user.Password) {
                            user.Password = hashlib.hash(user.Password);
                        } else {
                            delete user.Password;
                        }

                        notify.info(gettext('saving..'));
                        resource.users.save(user)
                            .then(function() {
                                notify.pop();
                                notify.success(gettext('user saved.'), 3000);
                                scope.onsave({user: user});
                            }, function(reason) {
                                notify.pop();
                                // todo(petr) render errors in form
                                notify.error(reason.data);
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
        .directive('sdUserName', ['em', function(em) {
            return {
                require: 'ngModel',
                link: function (scope, element, attrs, ctrl) {
                    ctrl.$parsers.unshift(function(viewValue) {
                        if (viewValue) {
                            em.getRepository('users').matching({where: {username: viewValue}}).then(function(result) {
                                ctrl.$setValidity('usernameavailable', result._items.length === 0);
                            });
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
