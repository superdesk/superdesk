define([], function() {
    'use strict';

    return function ListItemDirectiveFactory() {
        return {
            link: function(scope, element, attrs, controller, $transclude) {
                scope.$watch('item', function() {
                    var itemScope = scope.$parent.$parent.$new();
                    itemScope.item = scope.item;
                    $transclude(itemScope, function(clone) {
                        element.empty();
                        element.append(clone);
                    });
                });
            }
        };
    };
});
