define(['angular', 'require'], function(angular, require) {
    'use strict';

    angular.module('superdesk.items-common.directives', [])
        .directive('sdMediaBox', ['$position', function($position) {
            return {
                restrict: 'A',
                templateUrl: require.toUrl('./views/media-box.html'),
                link: function(scope, element, attrs) {
                    scope.$watch('extras.view', function(view) {
                        switch (view) {
                        case 'mlist':
                        case 'compact':
                            scope.itemTemplate = require.toUrl('./views/media-box-list.html');
                            break;
                        default:
                            scope.itemTemplate = require.toUrl('./views/media-box-grid.html');
                        }
                    });
                }
            };
        }])
        .directive('sdMediaBoxHover', ['$position', function($position) {
            return {
                replace: true,
                templateUrl: require.toUrl('./views/media-box-hover.html')
            };
        }])
        .directive('sdItemRendition', function() {
            return {
                templateUrl: require.toUrl('./views/item-rendition.html'),
                scope: {item: '=', rendition: '@'},
                link: function(scope, elem) {
                    scope.$watch('item.renditions[rendition].href', function(href) {
                        var figure = elem.find('figure'),
                            oldImg = figure.find('img').css('opacity', 0.5);
                        if (href) {
                            var img = new Image();
                            img.onload = function() {
                                if (oldImg.length) {
                                    oldImg.replaceWith(img);
                                } else {
                                    figure.prepend(img);
                                }
                            };

                            img.src = href;
                        }
                    });
                }
            };
        })
        .directive('sdHtmlPreview', ['$sce', function($sce) {
            return {
                scope: {sdHtmlPreview: '='},
                template: '<div ng-bind-html="html"></div>',
                link: function(scope, elem, attrs) {
                    scope.$watch('sdHtmlPreview', function(html) {
                        scope.html = $sce.trustAsHtml(html);
                    });
                }
            };
        }])
        .directive('sdProviderMenu', ['$location', function($location) {
            return {
                scope: {items: '='},
                templateUrl: require.toUrl('./views/provider-menu.html'),
                link: function(scope, element, attrs) {

                    scope.setProvider = function(provider) {
                        scope.selected = provider;
                        $location.search('provider', scope.selected);
                    };

                    scope.$watchCollection(function() {
                        return $location.search();
                    }, function(search) {
                        if (search.provider) {
                            scope.selected = search.provider;
                        }
                    });

                }
            };
        }])
        .directive('sdTabmodule', function() {
            return {
                templateUrl: require.toUrl('./views/tabmodule.html'),
                replace: true,
                transclude: true,
                scope: true,
                link: function($scope, element, attrs) {
                    $scope.title = attrs.title;
                    $scope.isOpen = attrs.open === 'true';
                    $scope.toggleModule = function() {
                        $scope.isOpen = !$scope.isOpen;
                    };
                }
            };
        });
});
