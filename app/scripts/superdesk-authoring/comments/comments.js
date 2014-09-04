
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

CommentsCtrl.$inject = ['$scope', 'commentsService', 'api', 'mentioUtil', '$q'];
function CommentsCtrl($scope, commentsService, api, mentioUtil, $q) {

    $scope.text = null;
    $scope.saveEnterFlag = false;
    $scope.$watch('item._id', reload);
    $scope.$on('changes in archive_comment', reload);
    $scope.users = null;

    $scope.saveOnEnter = function($event) {
        if (!$scope.saveEnterFlag || $event.keyCode !== ENTER || $event.shiftKey) {
            return;
        }
        $scope.save();
        return false;
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
        commentsService.fetch($scope.item._id).then(function() {
            $scope.comments = commentsService.comments;
        });
    }

    $scope.searchUsers = function(term) {
        var userlist = [];
        api.users.query()
        .then(function(result) {
            _.each(result._items, function(item) {
                if (item.display_name.toUpperCase().indexOf(term.toUpperCase()) >= 0) {
                    userlist.push(item);
                }
            });
            $scope.users = userlist;
            return $q.when(userlist);
        });
    };

    $scope.selectUser = function(user) {
        return '@' + user.username;
    };

}

angular.module('superdesk.authoring.comments', ['superdesk.authoring.widgets', 'mentio'])
    .config(['authoringWidgetsProvider', function(authoringWidgetsProvider) {
        authoringWidgetsProvider
            .widget('comments', {
                icon: 'comments',
                label: gettext('Comments'),
                template: 'scripts/superdesk-authoring/comments/views/comments-widget.html'
            });
    }])

    .config(['apiProvider', function(apiProvider) {
        apiProvider.api('item_comments', {
            type: 'http',
            backend: {rel: 'item_comments'}
        });
    }])

    .controller('CommentsWidgetCtrl', CommentsCtrl)
    .service('commentsService', CommentsService);

})();
