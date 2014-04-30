define(['lodash', 'require'], function(_, require) {
    'use strict';

    return ['scratchpad', function(scratchpad) {
        return {
            replace: true,
            require: '^sdSuperdeskView',
            templateUrl: require.toUrl('./views/scratchpad.html'),
            link: function(scope, element, attrs, ctrl) {
                scope.flags = ctrl.flags;
                scope.items = [];

                scope.toggle = function() {
                    scope.flags['scratchpad-open'] = !scope.flags['scratchpad-open'];
                };

                scope.sort = function() {
                    var newSort = _.pluck(_.pluck(element.find('div[data-index]'), 'dataset'), 'index');
                    scratchpad.sort(newSort);
                };

                scope.drop = function(item) {
                    if (item) {
                        scratchpad.addItem(item);
                    }
                };

                function update() {
                    scratchpad.getItems().then(function(items) {
                        scope.items = items;
                    });
                }

                scratchpad.addListener(update);
                update();
            }
        };
    }];
});
