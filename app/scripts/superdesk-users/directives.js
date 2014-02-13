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
                templateUrl: 'scripts/superdesk-users/views/user-details-pane.html',
                replace: true,
                scope: {
                    user: '='
                },
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
        .directive('sdUserEdit', function() {
            return {
                templateUrl: 'scripts/superdesk-users/views/edit-form.html',
                replace: true,
                scope: {
                    user: '='
                }
            };
        })
        .directive('sdUserPicture', function() {
            function getDefaultPicture() {
                return 'images/avatar_default.png';
            }

            return {
                scope: {src: '='},
                link: function (scope, element, attrs) {
                    scope.$watch('src', function (src) {
                        element.on('error', function (e) {
                            element.attr('title', gettext('Error when loading: ') + element.attr('src'));
                            element.attr('src', getDefaultPicture());
                        });

                        element.attr('src', src ? src : getDefaultPicture());
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
        }]);

});
