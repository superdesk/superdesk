define([
    'angular',
    'require'
], function(angular, require) {
    'use strict';

    var INGEST_EVENT = 'ingest:update';

    angular.module('superdesk.widgets.ingest', ['superdesk.authoring.widgets'])
        .config(['widgetsProvider', function(widgets) {
            widgets.widget('ingest', {
                label: 'Ingest',
                multiple: true,
                icon: 'ingest',
                max_sizex: 2,
                max_sizey: 2,
                sizex: 1,
                sizey: 2,
                thumbnail: require.toUrl('./thumbnail.png'),
                template: require.toUrl('./widget-ingest.html'),
                configurationTemplate: require.toUrl('./configuration.html'),
                configuration: {maxItems: 10, provider: 'all', search: '', updateInterval: 5},
                description: 'Ingest widget'
            });
        }])
        .config(['authoringWidgetsProvider', function(authoringWidgets) {
            authoringWidgets.widget('ingest', {
                label: gettext('Ingest'),
                icon: 'ingest',
                template: require.toUrl('./widget-ingest.html')
            });
        }])
        .factory('IngestWidgetSearchCriteria', ['es', function(es) {

            /**
             * Get filter to match items similar to given item
             */
            function moreLikeThis(item) {
                var filters = [];

                if (item.slugline) {
                    filters.push({term: {slugline: item.slugline}});
                }

                if (item.subject && item.subject.length) {
                    filters.push({terms: {'subject.code': _.pluck(item.subject, 'code')}});
                }

                return filters;
            }

            return function(config) {
                var params = {
                    q: config.search || null,
                    size: config.size || 10
                };

                var filters = [];
                if (config.provider && config.provider !== 'all') {
                    filters.push({term: {provider: config.provider}});
                }

                if (config.item && !config.search) {
                    var itemFilters = moreLikeThis(config.item);
                    if (itemFilters.length) {
                        filters.push({or: itemFilters});
                    } else {
                        params.q = config.item.headline || null;
                    }
                }

                angular.extend(this, es(params, filters));
                this.sort = [{firstcreated: 'desc'}];
            };
        }])
        .controller('IngestController', ['$location', '$scope', 'superdesk', 'api', 'IngestWidgetSearchCriteria',
        function ($location, $scope, superdesk, api, SearchCriteria) {
            var config;
            var refresh = _.debounce(_refresh, 1000);

            $scope.selected = null;

            $scope.$on(INGEST_EVENT, function() {
                refresh();
                $scope.$digest();
            });

            $scope.$watchGroup({
                provider: 'widget.configuration.provider',
                size: 'widget.configuration.maxItems',
                search: 'query || widget.configuration.search',
                item: 'item',
                headline: 'headline'
            }, function(vals) {
                config = vals || {};
                refresh();
            });

            function _refresh() {
                var criteria = new SearchCriteria(config);
                api.ingest.query({source: criteria}).then(function(items) {
                    $scope.items = items;
                });
            }

            $scope.view = function(item) {
                $scope.selected = item;
            };

            $scope.go = function(item) {
                $location.path('/workspace/ingest');
                $location.search('_id', item._id);
            };
        }])
        .controller('IngestConfigController', ['$scope', 'superdesk', 'api',
        function ($scope, superdesk, api) {
            api.ingest.query({source: {size: 0}}).then(function(items) {
                $scope.availableProviders = ['all'].concat(_.pluck(items._facets.provider.terms, 'term'));
            });

            $scope.notIn = function(haystack) {
                return function(needle) {
                    return haystack.indexOf(needle) === -1;
                };
            };
        }]);
});
