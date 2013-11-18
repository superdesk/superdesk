define([
    'lodash',
    'jquery',
    'angular',
    'moment',
    'd3'
], function(_, $, angular, moment, d3) {
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

                    scope.$watch('ui.view', function(view) {
                        switch(view) {
                        case 'list':
                            scope.itemTemplate = 'scripts/superdesk-items/views/media-box-list.html';
                            break;
                        default:
                            scope.itemTemplate = 'scripts/superdesk-items/views/media-box-grid.html';
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
        .directive('sdItemList', function($routeParams, $location, storage) {
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
                        view: $routeParams.view || 'grid'
                    };

                    var actions = attrs.actions.split(',');
                    scope.actions = _.zipObject(actions, _.range(1, actions.length + 1, 0));

                    scope.toggleCompact = function() {
                        scope.ui.compact = !scope.ui.compact;
                        storage.setItem('archive:compact', scope.ui.compact, true);
                    };

                    scope.setView = function(val) {
                        scope.view = val;
                        $location.search('view', val !== 'grid' ? val : null);
                    };

                    scope.preview = function(item) {
                        scope.previewItem = item;
                        scope.previewSingle = item;

                        if (item.type === 'composite') {
                            scope.previewSingle = null;
                            scope.previewItem.packageRefs = item.groups[_.findKey(item.groups,{id:'main'})].refs;
                        }
                    };

                }
            };
        })
        .directive('sdItemPreview', function(em) {
            return {
                templateUrl: 'scripts/superdesk-items/views/item-preview.html',
                replace: true,
                scope: {
                    item: '=',
                    previewSingle : '=previewitem'
                },
                link: function(scope, element, attrs) {
                    scope.closeEdit = function() {
                        scope.item = null;
                        scope.previewSingle = null;
                    };
                    scope.treepreview = function(item) {
                        scope.previewSingle = item;
                    };
                    scope.archive = function(item) {
                        em.create('archive', item).then(function() {
                            item.archived = true;
                        });
                    };
                }
            };
        })
        .directive('sdRef',function(em){
            return {
                link: function(scope, element, attrs) {
                    scope.$watch('ref', function(ref) {
                        em.getRepository('ingest').find(ref.residRef).then(function(item) {
                            scope.refItem = item;
                        });
                    });

                }
            };
        })
        .directive('sdProviderFilter', function($routeParams, $location, providerRepository) {
            return {
                scope: {items: '='},
                templateUrl: 'scripts/superdesk-items/views/provider-filter.html',
                link: function(scope, element, attrs) {
                    scope.activeProvider = $routeParams.provider || null;
                    scope.setProvider = function(provider) {
                        $location.search('provider', provider);
                    };
                }
            };
        })
        .directive('sdPieChart', function() {
            return {
                scope: {
                    terms: '='
                },
                link: function(scope, element, attrs) {

                    // todo define chart css
                    element
                        .css('background-color', '#fff')
                        .css('float', 'left')
                        .css('margin', '10px 0 0 10px');

                    var width = 320 * (attrs.x ? parseInt(attrs.x, 10) : 1),
                        height = 250 * (attrs.y ? parseInt(attrs.y, 10) : 1),
                        radius = Math.min(width, height) / 2;

                    var color = d3.scale.category10();

                    var arc = d3.svg.arc()
                        .outerRadius(radius - 10)
                        .innerRadius(radius * 8 / 13 / 2);

                    var sort = attrs.sort || null;
                    var pie = d3.layout.pie()
                        .value(function(d) { return d.count; })
                        .sort(sort ? function(a, b) { return d3.ascending(a[sort], b[sort]); } : null);

                    var svg = d3.select(element[0]).append('svg')
                        .attr('width', width)
                        .attr('height', height)
                        .append('g')
                        .attr('transform', 'translate(' + width / 2 + ',' + height / 2 + ')');

                    scope.$watch('terms', function(terms) {
                        var g = svg.selectAll('.arc')
                            .data(pie(terms))
                            .enter().append('g')
                            .attr('class', 'arc');

                        g.append('path')
                            .attr('d', arc)
                            .style('fill', function(d) { return color(d.data.term); });

                        g.append('text')
                            .attr('transform', function(d) { return 'translate(' + arc.centroid(d) + ')'; })
                            .attr('dy', '.35em')
                            .style('text-anchor', 'middle')
                            .text(function(d) { return d.data.term; });
                    });
                }
            };
        })
        .directive('sdHistogram', function() {
            return {
                scope: {
                    entries: '='
                },
                link: function(scope, element, attrs) {
                    // todo define chart css
                    element
                        .css('background-color', '#fff')
                        .css('float', 'left')
                        .css('margin', '10px 0 0 10px');

                    var width = 320 * (attrs.x ? parseInt(attrs.x, 10) : 1),
                        barHeight = 30,
                        x = d3.scale.linear().range([0, width - 10]);

                    var color = d3.scale.category10();

                    var svg = d3.select(element[0]).append('svg')
                        .attr('width', width);

                    scope.$watch('entries', function(entries) {
                        var data = _.last(entries, 24);
                        data.reverse();
                        x.domain([0, d3.max(data, function(d) { return d.count; })]);
                        svg.attr('height', barHeight * data.length + 5);

                        var bar = svg.selectAll('.bar')
                            .data(data)
                            .enter().append('g')
                            .attr('class', 'bar')
                            .attr('transform', function(d, i) { return 'translate(5,' + (5 + i * barHeight) + ')'; });

                        bar.append('rect')
                            .attr('width', function(d) { return x(d.count); })
                            .attr('height', barHeight - 1)
                            .style('fill', function(d) { return color(d.time); });

                        bar.append('text')
                            .attr('x', 3)
                            .attr('y', barHeight / 2)
                            .attr('dy', '.35em')
                            .text(function(d) { return d.count + ' / ' + moment.unix(d.time / 1000).format('HH:mm') + '+'; });
                    });
                }
            };
        });
});