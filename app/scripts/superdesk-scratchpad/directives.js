define(['lodash', 'angular', 'jquery'], function(_, angular, $) {
    'use strict';

    angular.module('superdesk.scratchpad.directives', [])
        .directive('sdScratchpad', ['scratchpadService', function(scratchpadService) {
            return {
                templateUrl: 'scripts/superdesk-scratchpad/views/scratchpad.html',
                replace: true,
                link: function(scope, element, attrs) {
                    scope.status = false;
                    scope.items = [];

                    scope.toggle = function() {
                        scope.status = !scope.status;
                        $('.main-background-container').toggleClass('scratchpad-open');
                    };

                    scope.update = function() {
                        scratchpadService.getItems().then(function(items) {
                            scope.items = items;
                        });
                    };
                    scope.sort = function() {
                        var newSort = _.pluck(_.pluck(element.find('div[data-index]'), 'dataset'), 'index');
                        scratchpadService.sort(newSort);
                    };
                    scope.drop = function(item) {
                        if (item) {
                            scratchpadService.addItem(item);
                        }
                    };

                    scratchpadService.addListener(function() {
                        scope.update();
                    });
                    scope.update();
                }
            };
        }]);
});
