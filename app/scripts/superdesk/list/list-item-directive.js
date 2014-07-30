define([], function() {
    'use strict';

    return function ListItemDirectiveFactory() {
        return {
            link: function(scope, element, attrs, controller, $transclude) {
                $transclude(scope, function(clone) {
                    element.empty();
                    element.append(clone);
                });
            }
        };
    };
});
