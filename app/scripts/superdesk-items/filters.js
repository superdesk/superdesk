define([
    'jquery',
    'angular'
], function($, angular) {
    'use strict';

    angular.module('superdesk.items.filters', []).
        filter('body', function() {
            return function(content) {
                var lines = $(content);
                var texts = [];
                for (var i = 0; i < lines.length; i++) {
                    var el = $(lines[i]);
                    if (el.is('p')) {
                        texts.push(el[0].outerHTML);
                    }
                }

                return texts.join('\n');
            };
        }).
        filter('mergeWords', function() {
            return function(array) {
                var subjectMerged = [];
                _.forEach(array, function(item) {
                    subjectMerged.push(item.name);
                });

                return subjectMerged.join(', ');
            };
        }).
        filter('trusted', function($sce) {
            return function(value) {
                return $sce.trustAsResourceUrl(value);
            };
        });
});