define([
    'lodash',
    'jquery',
    'angular',
    'moment',
    'd3'
], function(_, $, angular, moment, d3) {
    'use strict';

    angular.module('superdesk.items.directives', [])
        .directive('sdSearchbar', ['$location', '$routeParams', function($location, $routeParams) {
            return {
                scope: {
                    df: '@'
                },
                link: function(scope, element, attrs) {
                    element.addClass('searchbar searchbar-large');
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
        }])
        .directive('sdEditor', ['$sce', function($sce) {
            return {
                require: 'ngModel',
                template: '<div aloha class="editor" ng-bind-html="editorContent"></div>',
                link: function(scope, element, attrs, ngModel) {
                    ngModel.$render = function() {
                        scope.editorContent = $sce.trustAsHtml(ngModel.$viewValue);
                    };

                    scope.$on('texteditor-content-changed', function(e, je, a) {
                        scope.$apply(function() {
                            ngModel.$setViewValue(a.editable.getContents());
                        });
                    });
                }
            };
        }])
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
        .directive('sdTabmodule', function() {
            return {
                templateUrl: 'scripts/superdesk-items/views/tabmodule.html',
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
        })
        .directive('sdWordcount', function() {
            return {
                require: '?ngModel',
                link: function($scope, element, attrs, ngModel) {
                    ngModel.$render = function() {
                        if (ngModel.$viewValue !== undefined && ngModel.$viewValue !== null) {
                            var value = ngModel.$viewValue;
                            var regex = /\s+/gi;
                            var wordCount = value.trim().replace(regex, ' ').split(' ').length;
                            element.html(wordCount);
                        } else {
                            element.html(0);
                        }
                    };
                }
            };
        })
        .directive('sdContent', function() {
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
        .directive('sdMediaBox', ['$position', function($position) {
            return {
                restrict: 'A',
                templateUrl: 'scripts/superdesk-items/views/media-box.html',
                link: function(scope, element, attrs) {
                    scope.$watch('extras.view', function(view) {
                        switch (view) {
                        case 'mlist':
                        case 'compact':
                            scope.itemTemplate = 'scripts/superdesk-items/views/media-box-list.html';
                            break;
                        default:
                            scope.itemTemplate = 'scripts/superdesk-items/views/media-box-grid.html';
                        }
                    });
                }
            };
        }])
        .directive('sdMediaBoxHover', ['$position', function($position) {
            return {
                restrict: 'A',
                templateUrl: 'scripts/superdesk-items/views/media-box-hover.html',
                replace: true,
                link: function(scope, element, attrs) {
                }
            };
        }])
        .directive('sdItemList', ['$routeParams', '$location', 'storage', function($routeParams, $location, storage) {
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
                        compact: getSetting('ingest:compact', false),
                        view: getSetting('ingest:view', 'list')
                    };

                    var actions = (attrs.actions || '').split(',');
                    scope.actions = _.zipObject(actions, _.range(1, actions.length + 1, 0));

                    scope.toggleCompact = function() {
                        scope.ui.compact = !scope.ui.compact;
                        storage.setItem('ingest:compact', scope.ui.compact, true);
                    };

                    scope.setView = function(val) {
                        scope.ui.view = val;
                        storage.setItem('ingest:view', scope.ui.view, true);
                    };

                }
            };
        }])
        .directive('sdItemPreviewStatic', ['em', function(em) {
            return {
                replace: true,
                scope: {item: '='},
                templateUrl: 'scripts/superdesk-items/views/item-preview-static.html',
                link: function(scope, elem, attrs) {
                    // noop
                }
            };
        }])
        .directive('sdScrollVisible', ['$location', 'providerRepository', function($location, providerRepository) {
            return;
        }])
        .directive('sdImageLoader', function() {
            return {
                link: function(scope, element, attrs) {
                    var img, loadImage;
                    img = null;

                    loadImage = function() {

                        element[0].src = '';
                        $(element[0]).parent().addClass('loading');

                        img = new Image();
                        img.src = attrs.loadSrc;

                        img.onload = function() {
                            element[0].src = attrs.loadSrc;
                            $(element[0]).parent().removeClass('loading');
                        };
                    };

                    scope.$watch(function() { return attrs.loadSrc; }, function(newVal, oldVal) {
                        loadImage();
                    });
                }
            };
        })
        .directive('sdRef', ['em', function(em) {
            return {
                link: function(scope, element, attrs) {
                    scope.$watch('ref', function(ref) {
                        em.getRepository('ingest').find(ref.residRef).then(function(item) {
                            scope.refItem = item;
                        });
                    });

                }
            };
        }])
        .directive('sdProviderFilter', ['$routeParams', '$location', 'providerRepository',
        function($routeParams, $location, providerRepository) {
            return {
                scope: {items: '='},
                templateUrl: 'scripts/superdesk-items/views/provider-filter.html',
                link: function(scope, element, attrs) {
                    scope.$watch('items._facets', function(facets) {
                        if (facets) {
                            scope.facets = facets;
                            scope.activeProvider = scope.items.where('provider');
                        }
                    });

                    scope.setProvider = function(provider) {
                        scope.items.where('provider', provider);
                    };
                }
            };
        }])
        .directive('sdProviderMenu', function() {
            return {
                scope: {items: '=', selected: '='},
                templateUrl: 'scripts/superdesk-items/views/provider-menu.html',
                link: function(scope, element, attrs) {
                    scope.setProvider = function(provider) {
                        scope.selected = provider.term;
                    };
                }
            };
        })
        .directive('sdPieChart', ['colorSchemes', function(colorSchemes) {
            return {
                templateUrl: 'scripts/superdesk-items/views/chartBox.html',
                replace: true,
                scope: {
                    terms: '=',
                    head: '@',
                    theme: '@'
                },
                link: function(scope, element, attrs) {

                    var appendTarget = element[0].getElementsByClassName('block')[0];

                    var horizBlocks = attrs.x ? parseInt(attrs.x, 10) : 1;
                    var vertBlocks  = attrs.y ? parseInt(attrs.y, 10) : 1;

                    var graphSettings = {       //thightly depends on CSS
                        blockWidth: 320,
                        blockHeight: 250,
                        mergeSpaceLeft: 52,     //30 + 2 + 20
                        mergeSpaceBottom: 99   //30 + 2 + 20 + 47
                    };

                    var width = graphSettings.blockWidth * horizBlocks + graphSettings.mergeSpaceLeft * (horizBlocks - 1),
                        height = graphSettings.blockHeight * vertBlocks + graphSettings.mergeSpaceBottom * (vertBlocks - 1),
                        radius = Math.min(width, height) / 2;

                    colorSchemes.get(function(colorsData) {

                        var colorScheme = colorsData.schemes[0];

                        if (attrs.colors !== null) {
                            colorScheme = colorsData.schemes[_.findKey(colorsData.schemes, {name: attrs.colors})];
                        }

                        var colorScale = d3.scale.ordinal()
                                        .range(colorScheme.charts);

                        var arc = d3.svg.arc()
                            .outerRadius(radius - 10)
                            .innerRadius(radius * 8 / 13 / 2);

                        var sort = attrs.sort || null;
                        var pie = d3.layout.pie()
                            .value(function(d) { return d.count; })
                            .sort(sort ? function(a, b) { return d3.ascending(a[sort], b[sort]); } : null);

                        var svg = d3.select(appendTarget).append('svg')
                            .attr('width', width)
                            .attr('height', height)
                            .append('g')
                            .attr('transform', 'translate(' + width / 2 + ',' + height / 2 + ')');

                        scope.$watch('terms', function(terms) {

                            if (terms !== undefined) {
                                var g = svg.selectAll('.arc')
                                    .data(pie(terms))
                                    .enter().append('g')
                                    .attr('class', 'arc');
                                g.append('path')
                                    .attr('d', arc)
                                    .style('fill', function(d) { return colorScale(d.data.term); });
                                g.append('text')
                                    .attr('transform', function(d) { return 'translate(' + arc.centroid(d) + ')'; })
                                    .style('text-anchor', 'middle')
                                    .style('fill', colorScheme.text)
                                    .text(function(d) { return d.data.term; });
                            }

                        });
                    });
                }
            };
        }])
        .directive('sdPieChartDashboard', ['colorSchemes', function(colorSchemes) {
            return {
                replace: true,
                scope: {
                    terms: '=',
                    theme: '@',
                    colors: '='
                },
                link: function(scope, element, attrs) {

                    var appendTarget = element[0];
                    var horizBlocks = attrs.x ? parseInt(attrs.x, 10) : 1;
                    var vertBlocks  = attrs.y ? parseInt(attrs.y, 10) : 1;

                    var graphSettings = {       //thightly depends on CSS
                        blockWidth: 300,
                        blockHeight: 197,
                        mergeSpaceLeft: 60,     //30 + 2 + 20
                        mergeSpaceBottom: 99    //30 + 2 + 20 + 47
                    };

                    var width = graphSettings.blockWidth * horizBlocks + graphSettings.mergeSpaceLeft * (horizBlocks - 1),
                        height = graphSettings.blockHeight * vertBlocks + graphSettings.mergeSpaceBottom * (vertBlocks - 1),
                        radius = Math.min(width, height) / 2;

                    colorSchemes.get(function(colorsData) {

                        var colorScheme = colorsData.schemes[0];

                        var arc = d3.svg.arc()
                            .outerRadius(radius)
                            .innerRadius(radius * 8 / 13 / 2);

                        var sort = attrs.sort || null;
                        var pie = d3.layout.pie()
                            .value(function(d) { return d.count; })
                            .sort(sort ? function(a, b) { return d3.ascending(a[sort], b[sort]); } : null);

                        var svg = d3.select(appendTarget).append('svg')
                            .attr('width', width)
                            .attr('height', height)
                            .append('g')
                            .attr('transform', 'translate(' + width / 2 + ',' + height / 2 + ')');

                        scope.$watchCollection('[ terms, colors]', function(newData) {

                            if (newData[0] !== undefined) {

                                if (newData[1] !== null) {
                                    colorScheme = colorsData.schemes[_.findKey(colorsData.schemes, {name: newData[1]})];
                                }

                                var colorScale = d3.scale.ordinal()
                                        .range(colorScheme.charts);

                                svg.selectAll('.arc').remove();

                                var g = svg.selectAll('.arc')
                                    .data(pie(newData[0]))
                                    .enter().append('g')
                                    .attr('class', 'arc');

                                g.append('path')
                                    .attr('d', arc)
                                    .style('fill', function(d) { return colorScale(d.data.term); });

                                g.append('text')
                                    .attr('transform', function(d) { return 'translate(' + arc.centroid(d) + ')'; })
                                    .style('text-anchor', 'middle')
                                    .style('fill', colorScheme.text)
                                    .text(function(d) { return d.data.term; });
                            }

                        });
                    });
                }
            };
        }])
        .directive('sdHistogram', ['colorSchemes', function(colorSchemes) {
            return {
                templateUrl: 'scripts/superdesk-items/views/chartBox.html',
                replace: true,
                scope: {
                    entries: '=',
                    head: '@',
                    theme: '@'
                },
                link: function(scope, element, attrs) {

                    var horizBlocks = attrs.x ? parseInt(attrs.x, 10) : 1;
                    var vertBlocks  = attrs.y ? parseInt(attrs.y, 10) : 1;

                    var appendTarget = element[0].getElementsByClassName('block')[0];

                    var graphSettings = {       //thightly depends on CSS
                        blockWidth: 320,
                        blockHeight: 250,
                        mergeSpaceLeft: 52,     //30 + 2 + 20
                        mergeSpaceBottom: 99,   //30 + 2 + 20 + 47
                        horizontal: attrs.horizontal === 'true' ? true : false,
                        showText: attrs.text === 'false'  ? false : true
                    };

                    var width = graphSettings.blockWidth * horizBlocks + graphSettings.mergeSpaceLeft * (horizBlocks - 1),
                        height = graphSettings.blockHeight * vertBlocks + graphSettings.mergeSpaceBottom * (vertBlocks - 1),
                        dimension = graphSettings.horizontal ? width : height,
                        oDimension = graphSettings.horizontal ? height : width,
                        x = d3.scale.linear().range([0, oDimension]);

                    colorSchemes.get(function(colorsData) {

                        var colorScheme = colorsData.schemes[0];

                        if (attrs.colors !== null) {
                            colorScheme = colorsData.schemes[_.findKey(colorsData.schemes, {name: attrs.colors})];
                        }

                        var colorScale = d3.scale.ordinal()
                                        .range(colorScheme.charts);

                        var svg = d3.select(appendTarget).append('svg')
                            .attr('width', width)
                            .attr('height', height);

                        scope.$watch('entries', function(entries) {

                            var data = _.last(entries, 24);
                            data.reverse();
                            x.domain([0, d3.max(data, function(d) { return d.count; })]);

                            var barOuter = Math.floor(dimension / data.length);
                            var barSpace = Math.floor(barOuter * 0.2);
                            var barInner = barOuter - barSpace;

                            var bar = svg.selectAll('.bar')
                                .data(data)
                                .enter()
                                .append('g').attr('class', 'bar')
                                .style('fill', function(d) { return colorScale(d.time); });

                            if (graphSettings.horizontal) {
                                bar.attr('transform', function(d, i) { return 'translate(' + (i * barOuter) + ',0)'; })
                                    .append('rect')
                                        .attr('height', function(d) { return x(d.count); })
                                        .attr('width', barInner)
                                        .attr('y', function(d) { return (height - x(d.count)); });
                                if (graphSettings.showText) {
                                    bar.append('text')
                                    .style('fill', colorScheme.text)
                                    .text(function(d) { return d.count + ' / ' + moment.unix(d.time / 1000).format('HH:mm') + '+'; })
                                    .attr('transform', function(d, i) {
                                        return 'translate(' + (2 * barInner / 3) + ',' + (height - 5) + ')rotate(270)';
                                    });
                                }
                            } else {
                                bar.attr('transform', function(d, i) { return 'translate(0,' + (i * barOuter) + ')'; })
                                    .append('rect')
                                        .attr('width', function(d) { return x(d.count); })
                                        .attr('height', barInner);

                                if (graphSettings.showText) {
                                    bar.append('text')
                                        .attr('x', 5)
                                        .attr('y', barOuter / 2)
                                        .style('fill', colorScheme.text)
                                        .text(function(d) { return d.count + ' / ' + moment.unix(d.time / 1000).format('HH:mm') + '+'; });
                                }
                            }
                        });
                    });
                }
            };
        }])
        .directive('sdSource', ['$sce', function($sce) {
            var typeMap = {
                'video/mpeg': 'video/mp4'
            };

            return {
                scope: {
                    sdSource: '='
                },
                link: function(scope, element) {
                    scope.$watch('sdSource', function(source) {
                        element.empty();
                        if (source) {
                            angular.element('<source />')
                                .attr('type', typeMap[source.mimetype] || source.mimetype)
                                .attr('src', source.href)
                                .appendTo(element);
                        }
                    });
                }
            };
        }])
        .directive('sdArchiveLayout', function() {
            return {
                templateUrl: 'scripts/superdesk-items/views/item-list.html',
                link: function(scope, elem, attrs) {
                    scope.view = 'mgrid';

                    scope.preview = function(item) {
                        scope.previewItem = item;
                    };
                }
            };
        })
        .directive('sdSidebarLayout', ['$location', '$filter', function($location, $filter) {
            return {
                transclude: true,
                templateUrl: 'scripts/superdesk-items/views/sidebar.html',
                controller: ['$scope', function($scope) {

                    $scope.sidebar = false;
                    $scope.sidebarstick = true;

                    $scope.search = {
                        type: [
                            {
                                term: 'text',
                                checked: false,
                                count: 0
                            },
                            {
                                term: 'audio',
                                checked: false,
                                count: 0
                            },
                            {
                                term: 'video',
                                checked: false,
                                count: 0
                            },
                            {
                                term: 'picture',
                                checked: false,
                                count: 0
                            },
                            {
                                term: 'graphic',
                                checked: false,
                                count: 0
                            },
                            {
                                term: 'composite',
                                checked: false,
                                count: 0
                            }
                        ],
                        general: {
                            provider: null,
                            creditline: null,
                            place: null,
                            urgency: {
                                from: null,
                                to: null
                            },
                            versioncreated: {
                                from: null,
                                to: null
                            }
                        },
                        subjects: [],
                        places: []
                    };

                    //helper variables to handle large number of changes
                    $scope.versioncreated = {
                        startDate: null,
                        endDate: null,
                        init: false
                    };
                    $scope.urgency = {
                        from: 1,
                        to: 5
                    };

                    var createFilters = function() {

                        var filters = [];

                        function chainRange(obj, key) {
                            if (obj !== null && obj.from !== null && obj.to !== null) {
                                var rangefilter = {};
                                rangefilter[key] = {from: obj.from, to: obj.to};
                                filters.push({range: rangefilter});
                            }
                        }

                        function chain(val, key) {
                            if (val !== null && val !== '') {
                                var t = {};
                                t[key] = val;
                                filters.push({term: t});
                            }
                        }

                        //process content type
                        var contenttype = _.map(_.where($scope.search.type, {'checked': true}), function(t) { return t.term; });

                        //add content type filters as OR filters
                        if (contenttype.length > 0) {
                            filters.push({terms: {type: contenttype}});
                        }

                        //process general filters
                        _.forEach($scope.search.general, function(val, key) {
                            if (_.isObject(val)) {
                                chainRange(val, key);
                            } else {
                                chain(val, key);
                            }
                        });

                        //process subject filters
                        if ($scope.search.subjects.length > 0) {
                            filters.push({terms: {'subject.name': $scope.search.subjects, execution: 'and'}});
                        }

                        //process place filters
                        if ($scope.search.places.length > 0) {
                            filters.push({terms: {'place.name': $scope.search.places, execution: 'and'}});
                        }

                        //do filtering
                        if (filters.length > 0) {
                            $location.search('filter', angular.toJson({and: filters}));
                        } else {
                            $location.search('filter', null);
                        }

                    };

                    var createFiltersWrap = _.throttle(createFilters, 1000);
                    $scope.$watch('search', function() {
                        createFiltersWrap();
                    }, true);    //deep watch

                    //date filter handling
                    $scope.$watch('versioncreated', function(newVal) {
                        if (newVal.init === true) {
                            if (newVal.startDate !== null && newVal.endDate !== null) {
                                var start = $filter('dateString')(newVal.startDate);
                                var end = $filter('dateString')(newVal.endDate);
                                $scope.search.general.versioncreated = {from: start, to: end};
                            }
                        }
                    });

                    //urgency filter handling
                    function handleUrgency(urgency) {
                        var ufrom = Math.round(urgency.from);
                        var uto = Math.round(urgency.to);
                        if (ufrom !== 1 || uto !== 5) {
                            $scope.search.general.urgency.from = ufrom;
                            $scope.search.general.urgency.to = uto;
                        }
                    }

                    var handleUrgencyWrap = _.throttle(handleUrgency, 2000);

                    $scope.$watchCollection('urgency', function(newVal) {
                        handleUrgencyWrap(newVal);
                    });

                    $scope.$watchCollection('items', function() {
                        if ($scope.items._facets !== undefined) {
                            _.forEach($scope.items._facets.type.terms, function(type) {
                                _.extend(_.first(_.where($scope.search.type, {term: type.term})), type);
                            });
                        }
                    });

                    $scope.addSubject = function(item) {
                        if (!_.contains($scope.search.subjects, item.term.toLowerCase())) {
                            $scope.search.subjects.push(item.term);
                        }
                    };

                    $scope.removeSubject = function(item) {
                        $scope.search.subjects = _.without($scope.search.subjects, item);
                    };

                    $scope.addPlace = function(item) {
                        if (!_.contains($scope.search.places, item.term.toLowerCase())) {
                            $scope.search.places.push(item.term);
                        }
                    };

                    $scope.removePlace = function(item) {
                        $scope.search.places = _.without($scope.search.places, item);
                    };
                }]
            };
        }])
		.directive('sdFilterTypeahead', function() {
            return {
                scope: {
                    items: '=',
                    additem: '&'
                },
                templateUrl: 'scripts/superdesk-items/views/filter-typeahead.html',
                controller: ['$scope', function($scope) {

                    $scope.filtered = [];
                    $scope.searchterm = '';

                    $scope.searchItem = function(term) {
                        if (!term) {
                            $scope.filtered = [];
                        } else {
                            if ($scope.items !== undefined) {
                                $scope.filtered = $scope.items.filter(function(p) {
                                    return p.term.toLowerCase().indexOf(term.toLowerCase()) !== -1;
                                });
                            } else {
                                $scope.filtered = [];
                            }
                        }
                        return $scope.filtered;
                    };

                    $scope.selectItem = function(item) {
                        if (item) {
                            $scope.searchterm = '';
                            $scope.additem({item: item});
                        }
                    };

                }]
            };
        })
        .directive('sdWorkflow', ['superdesk', 'workqueue', function(superdesk, queue) {
            return {
                scope: true,
                link: function(scope, elem, attrs) {
                    scope.$watch(function() {
                        return queue.length;
                    }, function(len) {
                        scope.isActive = !!len;
                    });

                    scope.next = function() {
                        superdesk.intent('edit', 'archive', queue.active);
                    };
                }
            };
        }]);
});
