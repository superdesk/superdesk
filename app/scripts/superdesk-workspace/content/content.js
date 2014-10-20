(function() {
'use strict';

ContentCtrlFactory.$inject = ['api', 'superdesk', 'workqueue'];
function ContentCtrlFactory(api, superdesk, workqueue) {
    return function ContentCtrl($scope) {
        /**
         * Create an item and start editing it
         */
        this.create = function() {
            var item = {type: 'text'};
            api('archive')
                .save(item)
                .then(function() {
                    workqueue.add(item);
                    superdesk.intent('author', 'article', item);
                });
        };
    };
}

ViewsCtrlFactory.$inject = ['api', 'session'];
function ViewsCtrlFactory(api, session) {
    /**
     * Views controller
     */
    return function ViewsCtrl($scope) {
        var orig, desk, resource = api('content_view');

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
            try {
                this.flags.query = view.filter.query.filtered.query.query_string.query;
            } catch (err) {
                this.flags.query = null;
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

            this.edited.filter = {query: {filtered: {query: {query_string: {query: this.flags.query || '*'}}}}};

            this.edited.location = this.edited.location || 'archive'; // for now

            resource.save(orig, this.edited)
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

            return resource.query(criteria).then(angular.bind(this, function(response) {
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
        priority: 0,
        templateUrl: 'scripts/superdesk-workspace/content/views/desk-views.html',
        link: function(scope, elem, attrs) {
            var buttonLeft = elem.parent().find('.button-stack.left-stack');
            var buttonRight = elem.parent().find('.button-stack.right-stack');
            var viewsList = elem.find('ul');
            var _marginTop = 10;
            var _rowHeight = 32;

            scope.show = false;

            scope.$watch('views', function(newVal, oldVal) {
                refresh();
            }, true);

            scope.$watch('selectedDesk', function() {
                _.defer(function() {
                    scope.show = false;
                    refresh();
                });
            });

            scope.close = function() {
                var ulPos = viewsList.offset().top + _marginTop;
                var active = viewsList.find('.active');
                if (active.length) {
                    var elPos = active.offset().top;
                    if (elPos > ulPos) {
                        viewsList.css({
                            'margin-top': ulPos - elPos - _marginTop
                        });
                    }
                }
                scope.show = false;
            };

            scope.open = function() {
                viewsList.css({
                    'margin-top': -_marginTop
                });
                scope.show = true;
            };

            function refresh() {
                elem.css({
                    left: buttonLeft.outerWidth() - 1,
                    right: buttonRight.outerWidth() - 1
                });

                if (!viewsList.hasClass('compact')) {
                    scope.overload = viewsList.outerHeight() >= _rowHeight * 2;
                }

            }
        }
    };
}

angular.module('superdesk.workspace.content', [])
    .factory('ViewsCtrl', ViewsCtrlFactory)
    .factory('ContentCtrl', ContentCtrlFactory)
    .directive('sdDeskViews', DeskViewsDirective);
})();
