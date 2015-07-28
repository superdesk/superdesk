define(['angular'], function(angular) {
    'use strict';

    return angular.module('superdesk.typeahead.directives', []).
        /**
         * Typeahead direcitve
         *
         * Usage:
         *  <div sd-typeahead items="subjects" term="subjectTerm" search="searchSubjects(term)" select="selectSubject(item)">
         *      <ul>
         *          <li typeahead-item="s" ng-repeat="s in subjects">
         *              {{s.term}}
         *          </li>
         *      </ul>
         *  </div>
         *
         * Params:
         * @scope {Object} items - choice list
         * @scope {Object} term - search term
         * @scope {Boolen} alwaysVisible - list of posible choices always stay visible
         * @scope {Function} search - callback for filtering choice action
         * @scope {Function} select - callback for select item aciton
         *
         */
        directive('sdTypeahead', ['$timeout', function($timeout) {
            return {
                restrict: 'A',
                transclude: true,
                replace: true,
                templateUrl: 'scripts/superdesk/views/sdTypeahead.html',
                scope: {
                    search: '&',
                    select: '&',
                    items: '=',
                    term: '=',
                    alwaysVisible: '=',
                    disabled: '='
                },
                controller: ['$scope', function($scope) {
                    $scope.items = [];
                    $scope.hide = false;

                    this.activate = function(item) {
                        $scope.active = item;
                    };

                    this.activateNextItem = function() {
                        var index = $scope.items.indexOf($scope.active);
                        this.activate($scope.items[(index + 1) % $scope.items.length]);
                    };

                    this.activatePreviousItem = function() {
                        var index = $scope.items.indexOf($scope.active);
                        this.activate($scope.items[index === 0 ? $scope.items.length - 1 : index - 1]);
                    };

                    this.isActive = function(item) {
                        return $scope.active === item;
                    };

                    this.selectActive = function() {
                        this.select($scope.active);
                    };

                    this.select = function(item) {
                        $scope.hide = true;
                        $scope.focused = true;
                        $scope.select({item: item});
                    };

                    $scope.isVisible = function() {
                        return !$scope.hide && ($scope.focused || $scope.mousedOver) && ($scope.items.length > 0);
                    };

                    $scope.query = function() {
                        $scope.hide = false;
                        $scope.search({term: $scope.term});
                    };
                }],

                link: function(scope, element, attrs, controller) {

                    var $input = element.find('.input-term > input');
                    var $list = element.find('.item-list');

                    $input.bind('focus', function() {
                        scope.$apply(function() { scope.focused = true; });
                    });

                    $input.bind('blur', function() {
                        scope.$apply(function() { scope.focused = false; });
                    });

                    $list.bind('mouseover', function() {
                        scope.$apply(function() { scope.mousedOver = true; });
                    });

                    $list.bind('mouseleave', function() {
                        scope.$apply(function() { scope.mousedOver = false; });
                    });

                    $input.bind('keyup', function(e) {
                        if (e.keyCode === 13) {
                            scope.$apply(function() { controller.selectActive(); });
                        }

                        if (e.keyCode === 27) {
                            scope.$apply(function() { scope.hide = true; });
                        }
                    });

                    $input.bind('keydown', function(e) {
                        if (e.keyCode === 13 || e.keyCode === 27) {
                            e.preventDefault();
                        }

                        if (e.keyCode === 40) {
                            e.preventDefault();
                            scope.$apply(function() { controller.activateNextItem(); });
                        }

                        if (e.keyCode === 38) {
                            e.preventDefault();
                            scope.$apply(function() { controller.activatePreviousItem(); });
                        }
                    });

                    scope.$watch('items', function(items) {
                        controller.activate(items.length ? items[0] : null);
                    });

                    scope.$watch('focused', function(focused) {
                        if (focused) {
                            $timeout(function() { $input.focus(); }, 0, false);
                        }
                    });

                    scope.$watch('isVisible()', function(visible) {
                        if (visible || scope.alwaysVisible) {
                            $list.show();
                        } else {
                            $list.hide();
                        }
                    });
                }
            };
        }])
        .directive('typeaheadItem', function() {
            return {
                require: '^sdTypeahead',
                link: function(scope, element, attrs, controller) {

                    var item = scope.$eval(attrs.typeaheadItem);

                    scope.$watch(function() { return controller.isActive(item); }, function(active) {
                        if (active) {
                            element.addClass('active');
                        } else {
                            element.removeClass('active');
                        }
                    });

                    element.bind('mouseenter', function(e) {
                        scope.$apply(function() { controller.activate(item); });
                    });

                    element.bind('click', function(e) {
                        scope.$apply(function() { controller.select(item); });
                    });
                }
            };
        });
});
