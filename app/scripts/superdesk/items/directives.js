define([
    'jquery',
    'angular'
], function($, angular) {
    angular.module('superdesk.items.directives', []).
        directive('sdContent', function() {
            function getText(content) {
                var lines = $(content);
                var texts = [];
                for (var i = 0; i < lines.length; i++) {
                    var el = $(lines[i]);
                    if (el.is('p')) {
                        texts.push(el[0].outerHTML);
                    }
                }

                return texts.join("\n");
            };

            return {
                require: '?ngModel',
                link: function($scope, element, attrs, ngModel) {
                    ngModel.$render = function() {
                        element.html(getText(ngModel.$viewValue.content));
                    };
                }
            };
        }).
        directive('sdContenteditable', function() {
            return {
                require: 'ngModel',
                link: function($scope, element, attrs, ngModel) {
                    element.attr('contenteditable', 'true');

                    $(element).keyup(function(e) {
                        $scope.$apply(function() {
                            ngModel.$setViewValue(element.html());
                        });
                    });

                    ngModel.$render = function() {
                        element.html(ngModel.$viewValue);
                    }
                }
            };
        });
});