import {get, without, isEqual, isEmpty} from 'lodash';
import angular from 'angular';
import widgets from './widgets';
import packages from './package-manager/package-manager';
import {onChangeMiddleware} from 'superdesk-core/scripts/apps/authoring/authoring';
import {startApp} from 'superdesk-core/scripts/index';
import ansaIptc from '../extensions/ansaIptc/dist/extension';
import imageShortcuts from '../extensions/imageShortcuts/dist/extension';
import ansaArchive from '../extensions/ansa-archive';
import lineCountInAuthoringHeader from '../extensions/lineCountInAuthoringHeader/dist/extension';
import planningExtension from 'superdesk-planning/client/planning-extension/dist/extension';

import AnsaRelatedCtrl from './AnsaRelatedCtrl';

import './styles.scss';
import './package-manager/package-manager.scss';

const DEFAULT_GENRE = 'Article';

class MetasearchController {
    constructor($scope, $location, $timeout, metasearch, Keys, workspace) {
        this.query = $location.search().query || '';
        this.openSearch = true; // active on start
        this.metasearch = metasearch;
        this.location = $location;
        this.timeout = $timeout;
        this.Keys = Keys;

        this.maxItems = 10;

        this.categories = [
            {_id: '', label: 'General'},
            {_id: 'news', label: 'News'},
            {_id: 'social media', label: 'Social Media'},
            {_id: 'videos', label: 'Videos'},
            {_id: 'ansa', label: 'ANSA'},
            {_id: 'enciclopedia', label: 'Enciclopedia'},
        ];

        this.time_ranges = [
            {_id: 'day', label: 'Today'},
            {_id: 'week', label: 'Last Week'},
            {_id: 'month', label: 'Last Month'},
            {_id: '', label: 'Anytime'},
        ];

        $scope.$watch(() => workspace.item && workspace.item.slugline, (slugline, oldVal) => {
            if (!this.query || this.query === oldVal) {
                this.query = slugline;
                this.search();
            }
        });

        this.category = null;
        this.time_range = null;

        // init
        this.search();
    }

    toggle() {
        this.openSearch = !this.openSearch;
    }

    reset() {
        this.query = '';
        this.items = null;
    }

    setCategory(category) {
        this.category = category;
        this.search();
    }

    setTime(time) {
        this.time_range = time;
        this.search();
    }

    search(event) {
        if (event && event.which !== this.Keys.enter) {
            return;
        }

        this.category = this.category || '';
        this.time_range = this.time_range === null ? 'day' : this.time_range;
        this.usedQuery = null;

        if (this.query) {
            let params = {q: this.parseQuery(this.query), format: 'json', pageno: 1};

            this.items = null;
            this.loading = true;

            params.time_range = this.time_range;
            params.categories = this.category || 'general';

            this.metasearch.metasearch(params)
                .then((response) => {
                    this.page = 1;
                    this.results = response.data.results || [];
                    this.items = this.results.slice(0, this.maxItems);
                    this.loading = false;
                    this.finished = this.results.length < 11;
                    this.params = params;
                    this.updatePagination();
                    this.usedQuery = this.query;
                });
        }
    }

    parseQuery(query) {
        return (query || '')
            .split(' ')
            .filter((piece) => !!piece)
            .join(' AND ');
    }

    updatePagination() {
        this.hasPrev = this.page > 1;
        this.hasNext = this.page * this.maxItems + 1 < this.results.length;

        if (!this.hasNext && !this.finished) {
            this.items = null;
            this.loading = true;
            this.params.pageno++;
            this.metasearch.metasearch(this.params)
                .then((response) => {
                    this.loading = false;

                    if (!response.data.results || !response.data.results.length) {
                        this.finished = true;
                    } else {
                        this.results = this.results.concat(response.data.results);
                    }

                    // re-render
                    this.goto(this.page);
                });
        }
    }

    goto(page) {
        let start;

        this.page = page || 1;

        start = (this.page - 1) * this.maxItems;
        this.items = null;

        this.timeout(() => {
            this.items = this.results.slice(start, start + this.maxItems);
            this.updatePagination();
        }, 200);
    }
}

MetasearchController.$inject = [
    '$scope',
    '$location',
    '$timeout',
    'metasearch',
    'Keys',
    'authoringWorkspace',
];

function AnsaMetasearchItem(config, $http, $sce) {
    var firstTwitter = true;

    function getEmbedWidth(elem) {
        return Math.min(550, Math.floor(elem[0].getBoundingClientRect().width) - 50);
    }

    return {
        link: (scope, elem) => {
            elem.attr('draggable', true);

            // set item data on event
            elem.on('dragstart', (event) => {
                let dt = event.dataTransfer || event.originalEvent.dataTransfer;
                let link = document.createElement('a');

                link.href = scope.item.url;
                link.text = scope.item.title;
                dt.setData('text/html', link.outerHTML);
                dt.setData('text/uri-list', scope.item.url);
            });

            scope.$on('$destroy', () => {
                elem.off('dragstart');
            });

            if (scope.item.url.indexOf('https://twitter.com') === 0 && scope.item.url.indexOf('status') > 0) {
                scope.embed = true;
                $http.get(config.server.url.replace('/api', '/twitter/'),
                    {params: {url: scope.item.url}, omit_script: !firstTwitter})
                    .then((response) => {
                        scope.html = $sce.trustAsHtml(response.data.html);
                    });

                firstTwitter = false;
            }

            if (scope.item.url.indexOf('https://www.youtube.com/watch?v=') === 0) {
                scope.embed = true;
                scope.iframe = $sce.trustAsResourceUrl(
                    scope.item.url.replace('watch?v=', 'embed/').replace('www.', '')
                );
                scope.width = getEmbedWidth(elem);
                scope.height = Math.floor(scope.width / 3 * 2);
            }
        },
    };
}

AnsaMetasearchItem.$inject = ['config', '$http', '$sce'];

AnsaSemanticsCtrl.$inject = ['$scope', '$rootScope', 'api'];
function AnsaSemanticsCtrl($scope, $rootScope, api) {
    let save = (result) => {
        $scope.item.semantics = result.semantics;

        if (result.place && isEmpty($scope.item.place)) {
            $scope.item.place = result.place;
        }

        if (!isEmpty(result.subject)) {
            const subjects = $scope.item.subject || [];

            $scope.item.subject = subjects.concat(
                result.subject.filter(
                    (subject) => !subjects.find(
                        (selectedSubject) => (
                            selectedSubject.qcode === subject.qcode &&
                            (selectedSubject.scheme === subject.scheme || (
                                selectedSubject.scheme == null && subject.scheme == null
                            ))
                        )
                    ) && (subject.scheme !== 'products' || $scope.item.type === 'text')
                )
            );
        }

        if (result.slugline && isEmpty($scope.item.slugline)) {
            $scope.item.slugline = result.slugline;
        }

        if (result.keywords && isEmpty($scope.item.keywords)) {
            $scope.item.keywords = result.keywords;
        }

        $scope.save();
    };

    let init = () => {
        if ($scope.item.semantics) {
            this.data = angular.extend({}, $scope.item.semantics);
        } else {
            this.refresh();
        }
    };

    let text = (val) => {
        try {
            return angular.element(val).text();
        } catch (err) {
            return val || '';
        }
    };

    this.refresh = () => api.save('analysis', {
        lang: $scope.item.language === 'en' ? 'ENG' : 'ITA',
        title: $scope.item.headline || '',
        text: [
            text($scope.item.abstract),
            text($scope.item.body_html),
            $scope.item.description_text || '',
        ].join('\n'),
        abstract: '',
    }).then((result) => {
        this.data = result.semantics;
        save(result);
        broadcast(result.semantics);
    });

    this.remove = (term, category) => {
        this.data[category] = without(this.data[category], term);
        save({semantics: this.data});
        broadcast(this.data);
    };

    function broadcast(semantics) {
        $rootScope.$broadcast('semantics:update', semantics);
    }

    init();
}

function AnsaLiveSuggestions(workspace, metasearch) {
    function getArchiveQueries(semantics) {
        if (isEmpty(semantics)) {
            return [];
        }

        const queries = {};
        const fields = ['persons', 'organizations', 'places', 'mainGroups', 'mainLemmas', 'iptcDomains'];

        fields.forEach((field) => {
            if (isEmpty(semantics[field])) {
                return;
            }

            semantics[field].forEach((val) => {
                queries[val] = true;
            });
        });

        return Object.keys(queries);
    }

    return {
        controller: 'MetasearchCtrl',
        controllerAs: 'metasearch',
        template: require('./views/ansa-live-suggestions.html'),
        link: (scope, elem, attrs, ctrl) => {
            scope.$watch(() => workspace.item && workspace.item.semantics, refresh);
            scope.$on('semantics:update', (event, semantics) => {
                refresh(semantics);
            });

            function refresh(semantics) {
                scope.item = workspace.item;
                scope.semantics = semantics;
                scope.suggestions = null;
                scope.archiveQueries = getArchiveQueries(semantics);
                scope.closeSearch();
            }

            scope.toggleInfo = (val) => {
                scope.loading = true;
                metasearch.suggest(val)
                    .then((response) => {
                        scope.suggestions = response.data;
                        if (isEmpty(scope.suggestions)) {
                            scope.suggestions = [val];
                        }
                    })
                    .finally(() => {
                        scope.loading = false;
                    });
            };

            scope.startSearch = (query) => {
                ctrl.query = query;
                ctrl.search();
                scope.searchEnabled = true;
            };

            scope.closeSearch = () => {
                scope.searchEnabled = false;
                ctrl.items = null;
            };

            scope.copy = ($event) => {
                let range = document.createRange();
                let selection = document.getSelection();

                range.selectNodeContents($event.target);
                selection.removeAllRanges();
                selection.addRange(range);
                document.execCommand('copy');
                selection.removeAllRanges();
            };
        },
    };
}

AnsaLiveSuggestions.$inject = ['authoringWorkspace', 'metasearch'];

function MetasearchFactory($http, config) {
    let url = config.server.url.replace('/api', '/metasearch') + '/';

    class MetasearchService {
        metasearch(params) {
            return $http.get(url, {params: params});
        }

        suggest(word) {
            return $http.get(url + 'autocompleter', {params: {q: word}});
        }
    }

    return new MetasearchService();
}

MetasearchFactory.$inject = ['$http', 'config'];

function AnsaMetasearchResults() {
    return {
        template: require('./views/ansa-metasearch-results.html'),
    };
}

function AnsaMetasearchDropdown() {
    return {
        template: require('./views/ansa-metasearch-dropdown.html'),
    };
}

AnsaRepoDropdown.$inject = ['api', '$filter', '$location', '$rootScope'];
function AnsaRepoDropdown(api, $filter, $location, $rootScope) {
    class AnsaRepoDropdownController {
        constructor($scope) {
            this.scope = $scope;
            this.fetchProviders();
        }

        fetchProviders() {
            return api.search_providers.query({max_results: 200})
                .then((result) => {
                    this.providers = $filter('sortByName')(result._items, 'search_provider');
                    this.active = this.providers.find((provider) => $location.search().repo === provider._id);
                });
        }

        toggle(provider) {
            this.active = provider;
            if (provider) {
                $location.search('repo', provider._id);
                this.scope.$applyAsync(() => angular.extend(this.scope.repo, {
                    ingest: false,
                    archive: false,
                    published: false,
                    archived: false,
                    search: provider._id,
                }));
                $rootScope.$broadcast('aggregations:changed');
            } else {
                $location.search('repo', null);
                this.scope.$applyAsync(() => {
                    angular.extend(this.scope.repo, {
                        ingest: true,
                        archive: true,
                        published: true,
                        archived: true,
                        search: 'local',
                    });
                });
            }
        }
    }

    AnsaRepoDropdownController.$inject = ['$scope'];

    return {
        controller: AnsaRepoDropdownController,
        controllerAs: 'repos',
    };
}

AnsaSearchPanelController.$inject = [];
function AnsaSearchPanelController() {
    this.categories = [
        'ACE',
        'CLJ',
        'DIS',
        'EBF',
        'EDU',
        'ENV',
        'FIN',
        'HTH',
        'HUM',
    ];

    this.fields = [
        {name: 'title', label: 'Title'},
        {name: 'text', label: 'Text'},
        {name: 'place', label: 'Place'},
        {name: 'author', label: 'Author'},
        {name: 'creditline', label: 'Credits'},
        {name: 'subcategory', label: 'Subcategory'},
    ];

    this.selectedCategories = {};

    this.updateCategory = (meta) => {
        meta.category = Object.keys(this.selectedCategories).filter((category) => !!this.selectedCategories[category]);
    };
}

// from superdesk-core/scripts/apps/authoring/media/MediaCopyMetadataDirective.ts
function getMediaMetadata(metadata, fields) {
    const output = {extra: {}};

    if (metadata == null) {
        return output;
    }

    fields.forEach((field) => {
        if (field.extra) {
            if (metadata.extra != null && metadata.extra[field.field] != null) {
                output.extra[field.field] = metadata.extra[field.field];
            }
        } else if (metadata[field.field] != null) {
            output[field.field] = metadata[field.field];
        }
    });

    return output;
}

export default angular.module('ansa.superdesk', [
    widgets.name,
    packages.name,
    'superdesk.apps.workspace.menu',
])
    .factory('metasearch', MetasearchFactory)
    .controller('MetasearchCtrl', MetasearchController)
    .controller('AnsaSemanticsCtrl', AnsaSemanticsCtrl)
    .controller('AnsaRelatedCtrl', AnsaRelatedCtrl)
    .controller('AnsaSearchPanel', AnsaSearchPanelController)
    .directive('ansaMetasearchItem', AnsaMetasearchItem)
    .directive('ansaLiveSuggestions', AnsaLiveSuggestions)
    .directive('ansaMetasearchResults', AnsaMetasearchResults)
    .directive('ansaMetasearchDropdown', AnsaMetasearchDropdown)
    .directive('ansaRepoDropdown', AnsaRepoDropdown)
    .config(['superdeskProvider', 'workspaceMenuProvider', (superdeskProvider, workspaceMenuProvider) => {
        superdeskProvider.activity('/workspace/metasearch', {
            label: gettext('Metasearch'),
            priority: 100,
            template: require('./views/metasearch.html'),
            topTemplateUrl: 'scripts/apps/dashboard/views/workspace-topnav.html',
            sideTemplateUrl: 'scripts/apps/workspace/views/workspace-sidenav.html',
        });

        superdeskProvider.activity('/workspace/assistant', {
            label: gettext('Live assistant'),
            priority: 200,
            template: require('./views/live-assistant.html'),
            topTemplateUrl: 'scripts/apps/dashboard/views/workspace-topnav.html',
            sideTemplateUrl: 'scripts/apps/workspace/views/workspace-sidenav.html',
        });

        superdeskProvider.activity('/ansa/map', {
            label: gettext('Superdesk aiNews'),
            priority: 300,
            template: require('./views/ansa-map.html'),
            topTemplateUrl: 'scripts/apps/dashboard/views/workspace-topnav.html',
            sideTemplateUrl: 'scripts/apps/workspace/views/workspace-sidenav.html',
        });

        workspaceMenuProvider
            .item({
                if: 'privileges.ansa_metasearch',
                href: '/workspace/metasearch',
                label: 'Metasearch',
                icon: 'meta-search',
                shortcut: 'alt+s',
                order: 910,
            })
            .item({
                if: 'privileges.ansa_live_assistant',
                href: '/workspace/assistant',
                label: 'Live assistant',
                icon: 'live',
                order: 920,
                shortcut: 'alt+l',
            })
            .item({
                if: 'privileges.ansa_ai_news',
                href: '/ansa/map',
                label: 'aiNews',
                icon: 'web',
                order: 930,
                group: 'map',
                shortcut: 'alt+a',
            });

        superdeskProvider.activity('copy-metadata', {
            label: gettext('Copy Metadata'),
            icon: 'copy',
            monitor: true,
            controller: ['data', '$controller', '$rootScope', function(data, $controller, $rootScope) {
                const ctrl = $controller('MediaFieldsController');
                const stopWatch = $rootScope.$watch(() => ctrl.fields, (fields) => {
                    if (fields) {
                        stopWatch();
                        localStorage.setItem('metadata:items', JSON.stringify(getMediaMetadata(data.item, fields)));
                    }
                });
            }],
            filters: [{action: 'list', type: 'archive'}],
            condition: (item) => item.type === 'picture',
        });
    }])
    // ansa core templates override
    .run(['$templateCache', ($templateCache) => {
        $templateCache.put(
            'scripts/apps/authoring/packages/views/packages-widget.html',
            require('./views/packages-widget.html')
        );

        $templateCache.put(
            'search-panel-ansa.html',
            require('./views/search-panel.html')
        );
    }])

    .run(['$rootScope', 'metadata', 'deployConfig', ($rootScope, metadata, deployConfig) => {
        let lastGenre = null;
        let prev = {};

        onChangeMiddleware.push(({item, original}) => {
            const headline = item.headline || '';
            const hasPlus = headline.includes('+');
            let updated = false;

            if (prev === null || prev._id !== original._id) {
                prev = original;
            }

            if (item.priority === 2 && prev.priority !== 2 && !hasPlus) {
                item.headline = '++ ' + headline + ' ++';
                updated = true;
            } else if (item.priority !== 2 && (prev.priority == null || prev.priority === 2) && hasPlus) {
                item.headline = headline.replace('++ ', '').replace(' ++', '');
                updated = true;
            }

            // set profile by priority SDANSA-446
            if (item.priority && prev.priority !== item.priority) {
                const priorityToProfileConfig = get(deployConfig, 'config.ansa.priority_to_profile_mapping') || {};

                if (priorityToProfileConfig[item.priority] && item.profile !== priorityToProfileConfig[item.priority]) {
                    item.profile = priorityToProfileConfig[item.priority];
                    updated = true;
                }
            }

            if (lastGenre == null) {
                lastGenre = original.genre || [];
            }

            const isSelected = (genre) => item.genre.find((_genre) => _genre.qcode === genre.qcode) != null;
            const wasSelected = (genre) => lastGenre.find((_genre) => _genre.qcode === genre.qcode) != null;

            if (!isEqual(get(item.genre, '0.name'), get(lastGenre, '0.name'))) {
                const genres = metadata.values.genre.concat();

                // remove removed
                genres.filter((genre) => wasSelected(genre) && !isSelected(genre))
                    .forEach((genre) => {
                        if (item.headline.startsWith(genre.name)) {
                            item.headline = item.headline.slice(genre.name.length).trim();
                            updated = true;
                        }
                    });

                // add new
                genres.filter((genre) => isSelected(genre) && !wasSelected(genre) && genre.qcode !== DEFAULT_GENRE)
                    .forEach((genre) => {
                        if (!item.headline.startsWith(genre.name)) {
                            item.headline = genre.name + ' ' + item.headline;
                            updated = true;
                        }
                    });
            }

            lastGenre = item.genre || []; // not set to null to avoid reseting to original

            if (updated) { // update editor3
                $rootScope.$broadcast('macro:refreshField', 'headline', item.headline, {skipOnChange: false});
            }

            prev = Object.assign({}, item);
        });
    }])
;

setTimeout(() => {
    startApp(
        [
            ansaIptc,
            imageShortcuts,
            planningExtension,
            ansaArchive,
            lineCountInAuthoringHeader,
        ],
        {},
        {
            countLines: (plainText, lineLength) =>
                plainText
                    .split('\n')
                    .reduce((sum, line) => sum + (line.length > 0 ? Math.ceil(line.length / lineLength) : 1), 0),
        }
    );
});
