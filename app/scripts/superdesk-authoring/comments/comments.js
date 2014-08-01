
(function() {

'use strict';

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

        return api.item_comments.query(criteria).then(function(result) {
            this.comments = result._items;
        }.bind(this));
    };

    this.save = function(comment) {
        return api.item_comments.save(comment);
    };
}

CommentsCtrl.$inject = ['$scope', 'commentsService'];
function CommentsCtrl($scope, commentsService) {
    $scope.text = null;

    $scope.save = function() {
        commentsService.save({
            text: $scope.text,
            item: $scope.item._id
        }).then(function() {
            $scope.text = null;
        }).then(reload);
    };

    $scope.$watch('item._id', reload);
    $scope.$on('changes in archive_comment', reload);

    function reload() {
        commentsService.fetch($scope.item._id).then(function() {
            $scope.comments = commentsService.comments;
        });
    }
}

angular.module('superdesk.authoring.comments', ['superdesk.authoring.widgets'])
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
