define([
    'lodash',
    'angular',
    'require',
    'd3'
], function(_, angular, require, d3) {
    'use strict';

    return angular.module('superdesk.archive.directives', [])
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
        }]);
});
