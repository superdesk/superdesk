(function() {
'use strict';

ViewsCtrlFactory.$inject = ['api', 'session'];
function ViewsCtrlFactory(api, session) {
    /**
     * Views controller
     */
    return function ViewsCtrl($scope) {
        var orig, desk;

        this.flags = {};
        this.views = null;
        this.selected = null;

        // select a view as active
        this.select = function(view) {
            this.selected = view || null;
        };

        // pick given view for editing
        this.edit = function(view) {
            this.edited = _.create(view);
            orig = view;

            this.flags = {};
            if (view.filter && view.filter.query) {
                this.flags.query = view.filter.query.query_string.query;
            }

            this._issues = null;
        };

        // create a new view
        this.create = function() {
            this.edit({});
        };

        // cancel creating a new view
        this.cancel = function() {
            this.edited = null;
        };

        // save edited view
        this.save = function() {
            if (this.flags.is_desk) {
                this.edited.desk = desk;
            }

            this.edited.filter = {query: {query_string: {query: this.flags.query || '*'}}};

            this.edited.location = this.edited.location || 'archive'; // for now

            api.views.save(orig, this.edited)
                .then(angular.bind(this, function() {
                    this.reload();
                    this.cancel();
                }), angular.bind(this, function(response) {
                    this._issues = response._issues;
                }));
        };

        // reload list of views
        this.reload = function() {
            var criteria = {};

            if (desk) {
                criteria.where = {desk: desk};
            } else {
                criteria.where = {user: session.identity._id};
            }

            return api.views.query(criteria).then(angular.bind(this, function(response) {
                this.views = response._items;
            }));
        };

        $scope.$watch('selectedDesk', angular.bind(this, function(_desk) {
            desk = _desk ? _desk._id : null;
            this.select();
            this.reload();
        }));
    };
}

function DeskViewsDirective() {
    return {
        templateUrl: 'scripts/superdesk-workspace/content/views/desk-views.html'
    };
}

angular.module('superdesk.workspace.content', [])
    .factory('ViewsCtrl', ViewsCtrlFactory)
    .directive('sdDeskViews', DeskViewsDirective)

    .config(['apiProvider', function(apiProvider) {
        apiProvider.api('views', {
            type: 'http',
            backend: {rel: 'content_view'}
        });
    }]);

})();
