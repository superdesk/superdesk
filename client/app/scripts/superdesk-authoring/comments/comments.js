
(function() {

'use strict';

var ENTER = 13;

CommentsService.$inject = ['api'];
function CommentsService(api) {

    this.comments = null;

    this.fetch = function(item) {
        var criteria = {
            where: {
                item: item
            },
            embedded: {user: 1}
        };

        return api.item_comments.query(criteria)
            .then(angular.bind(this, function(result) {
                this.comments = result._items;
            }));
    };

    this.save = function(comment) {
        return api.item_comments.save(comment);
    };
}

CommentsCtrl.$inject = ['$scope', '$routeParams', 'commentsService', 'api', '$q'];
function CommentsCtrl($scope, $routeParams, commentsService, api, $q) {

    $scope.text = null;
    $scope.saveEnterFlag = false;
    $scope.$watch('item._id', reload);
    $scope.users = [];

    $scope.saveOnEnter = function($event) {
        if (!$scope.saveEnterFlag || $event.keyCode !== ENTER || $event.shiftKey) {
            return;
        }
        $scope.save();
    };

    $scope.save = function() {
        var text = $scope.text || '';
        if (!text.length) {
            return;
        }

        $scope.text = '';
        $scope.flags = {saving: true};

        commentsService.save({
            text: text,
            item: $scope.item._id
        }).then(reload);
    };

    $scope.cancel = function() {
        $scope.text = '';
    };

    function reload() {
        if ($scope.item) {
            commentsService.fetch($scope.item._id).then(function() {
                $scope.comments = commentsService.comments;
            });
        }
    }

    $scope.$on('item:comment', function(e, data) {
        if (data.item === $scope.item.guid) {
            reload();
        }
    });

    function setActiveComment() {
        $scope.active = $routeParams.comments || null;
    }

    $scope.$on('$locationChangeSuccess', setActiveComment);
    setActiveComment();
}

CommentTextDirective.$inject = ['$compile'];
function CommentTextDirective($compile) {
    return {
        scope: {
            comment: '='
        },
        link: function(scope, element, attrs) {

            var html;

            //replace new lines with paragraphs
            html  = attrs.text.replace(/(?:\r\n|\r|\n)/g, '</p><p>');

            //map user mentions
            var mentioned = html.match(/\@([a-zA-Z0-9-_.]\w+)/g);
            _.each(mentioned, function(token) {
                var username = token.substring(1, token.length);
                if (scope.comment.mentioned_users && scope.comment.mentioned_users[username]) {
                    html = html.replace(token,
                    '<i sd-user-info data-user="' + scope.comment.mentioned_users[username] + '">' + token + '</i>');
                }
            });

            //build element
            element.html('<p><b>' + attrs.name + '</b> : ' + html + '</p>');

            $compile(element.contents())(scope);
        }
    };
}

angular.module('superdesk.authoring.comments', ['superdesk.authoring.widgets', 'mentio', 'superdesk.api'])
    .config(['authoringWidgetsProvider', function(authoringWidgetsProvider) {
        authoringWidgetsProvider
            .widget('comments', {
                icon: 'comments',
                label: gettext('Comments'),
                template: 'scripts/superdesk-authoring/comments/views/comments-widget.html',
                order: 3,
                side: 'right',
                display: {authoring: true, packages: true, legalArchive: false}
            });
    }])

    .config(['apiProvider', function(apiProvider) {
        apiProvider.api('item_comments', {
            type: 'http',
            backend: {rel: 'item_comments'}
        });
    }])

    .controller('CommentsWidgetCtrl', CommentsCtrl)
    .service('commentsService', CommentsService)
    .directive('sdCommentText', CommentTextDirective);

})();
