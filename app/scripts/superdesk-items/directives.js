define([
    'lodash',
    'jquery',
    'angular',
    'moment'
], function(_, $, angular, moment) {
    'use strict';

    angular.module('superdesk.items.directives', ['ui.bootstrap']).
        filter('reldate', function() {
            return function(date) {
                return moment(date).fromNow();
            };
        }).
        directive('sdSearchbar', function($location, $routeParams) {
            return {
                scope: {
                    df: '@'
                },
                link: function(scope, element, attrs) {
                    element.attr('name', 'searchbar');
                    element.attr('autofocus', 'autofocus');
                    element.addClass('searchbar-container');
                    element.val($routeParams.q || '');

                    element.change(function() {
                        scope.$apply(function() {
                            var query = element.val();
                            if (query && query.length > 2) {
                                $location.search('q', query);
                                $location.search('page', null);
                                $location.search('df', scope.df);
                            } else if (query.length === 0) {
                                $location.search('q', null);
                                $location.search('page', null);
                                $location.search('df', null);
                            }
                        });
                    });
                }
            };
        }).
        directive('sdHtml', function($sce) {
            return {
                require: '?ngModel',
                link: function($scope, element, attrs, ngModel) {
                    ngModel.$render = function() {
                        element.prepend(ngModel.$viewValue);
                    };
                }
            };
        }).
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

                return texts.join('\n');
            }

            return {
                require: '?ngModel',
                link: function($scope, element, attrs, ngModel) {
                    ngModel.$render = function() {
                        element.html(getText(ngModel.$viewValue.content));
                    };
                }
            };
        })
        .directive('sdMediaBox', function($position){
            return {
                restrict : 'A',
                template: '<div ng-include="itemTemplate"></div>',
                link: function(scope, element, attrs) {

                    scope.$watch('ui.grid', function(isGrid) {
                        if (isGrid) {
                            scope.itemTemplate = 'scripts/superdesk-items/views/media-box-grid.html';
                        } else {
                            scope.itemTemplate = 'scripts/superdesk-items/views/media-box-list.html';
                        }
                    });

                    scope.hoverItem = function(item) {
                        var pos = $position.position(element.find('.media-box'));
                        scope.selectedItem.item = item;
                        scope.selectedItem.position = {left: pos.left - 9, top: pos.top - 15};
                        scope.selectedItem.show = true;
                    };
                }
            };
        })
        .directive('sdMediaBoxHover', function($position){
            return {
                restrict : 'A',
                templateUrl : 'scripts/superdesk-items/views/media-box-hover.html',
                replace : true,
                link: function(scope, element, attrs) {
                }
            };
        })
        .directive('sdItemList', function(storage) {
            return {
                templateUrl: 'scripts/superdesk-items/views/item-list.html',
                link: function(scope, element, attrs) {
                    function getSetting(key, def) {
                        var val = storage.getItem(key);
                        return (val === null) ? def : val;
                    }

                    scope.selectedItem = {
                        item: null,
                        position: {
                            left: 0,
                            top: 0
                        },
                        show: false
                    };

                    scope.ui = {
                        compact: getSetting('archive:compact', false),
                        grid: getSetting('archive:grid', true)
                    };

                    var actions = attrs.actions.split(',');
                    scope.actions = _.zipObject(actions, _.range(1, actions.length + 1, 0));

                    scope.toggleCompact = function() {
                        scope.ui.compact = !scope.ui.compact;
                        storage.setItem('archive:compact', scope.ui.compact, true);
                    };

                    scope.setGridView = function(val) {
                        scope.ui.grid = !!val;
                        storage.setItem('archive:grid', scope.ui.grid, true);
                    };

                    scope.preview = function(item) {
                        scope.editItem = item;
                    };
                }
            };
        })
        .directive('sdItemPreview', function() {
            return {
                templateUrl: 'scripts/superdesk-items/views/item-preview.html',
                replace: true,
                scope: {
                    item: '='
                },
                link: function(scope, element, attrs) {
                    scope.closeEdit = function() {
                        scope.item = null;
                    };
                }
            };
        })
        .directive('sdProviderFilter', function($routeParams, $location, providerRepository) {
            return {
                scope: {},
                templateUrl: 'scripts/superdesk-items/views/provider-filter.html',
                link: function(scope, element, attrs) {
                    providerRepository.findAll().then(function(providers) {
                        scope.providers = providers;

                        if ('provider' in $routeParams) {
                            scope.activeProvider = _.find(providers._items, {_id: $routeParams.provider});
                        }

                        scope.set_provider = function(provider_id) {
                            $location.search('provider', provider_id);
                        };
                    });
                }
            };
        });
});