define(['lodash', 'angular'], function(_, angular) {
    'use strict';

    angular.module('superdesk.users.providers', [])
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

        }]);
});
