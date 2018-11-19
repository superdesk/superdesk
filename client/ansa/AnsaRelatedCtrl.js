import {max, isEmpty} from 'lodash';

// must match gallery field id
const GALLERY = 'photoGallery';

AnsaRelatedCtrl.$inject = ['$scope', 'api', 'storage', 'Keys', 'mediaIdGenerator'];
export default function AnsaRelatedCtrl($scope, api, storage, Keys, mediaIdGenerator) {
    const search = () => {
        if (!$scope.item.semantics || !$scope.item.semantics.iptcCodes) {
            this.items = [];
            return;
        }

        this.items = null;

        let filters = [];
        let semantics = $scope.item.semantics;
        let keys = ['persons', 'organizations'];
        let namespace = (key) => 'semantics.' + key;

        keys.forEach((key) => {
            if (semantics[key] && semantics[key].length) {
                semantics[key].forEach((val) => {
                    let f = {};

                    f[namespace(key)] = val;
                    filters.push({match_phrase: f});
                });
            }
        });

        let pictureFilters = [];
        let prefixes = {};

        if (!isEmpty(semantics.iptcCodes)) {
            semantics.iptcCodes.forEach((code) => {
                let prefix = code.substr(0, 2);

                if (!prefixes[prefix]) {
                    prefixes[prefix] = 1;
                    pictureFilters.push({prefix: {'semantics.iptcCodes': prefix}});
                }
            });
        }

        let query = {
            bool: {
                must_not: {term: {_id: $scope.item._id}},
                should: [],
            },
        };

        if (this.activeFilter === 'text') {
            angular.extend(query.bool, {
                must: [
                    {term: {type: 'text'}},
                    {terms: {'semantics.iptcCodes': semantics.iptcCodes}},
                ],
                should: filters,
                minimum_should_match: 1,
            });
        } else {
            angular.extend(query.bool, {
                must: pictureFilters.concat([{term: {type: this.activeFilter}}]),
                should: filters,
                minimum_should_match: 1,
            });
        }

        if (this.query) {
            query = {
                bool: {
                    must: [
                        {term: {type: this.activeFilter}},
                        {query_string: {query: this.query, lenient: true}},
                    ],
                },
            };
        }

        this.apiQuery(query);
    };

    this.activeFilter = storage.getItem('ansa.related.filter') || 'text';

    this.filter = (activeFilter) => {
        this.activeFilter = activeFilter;
        storage.setItem('ansa.related.filter', activeFilter);
        search();
    };

    this.searchOnEnter = (event) => {
        if (event.which === Keys.enter) {
            search();
        }
    };

    this.apiQuery = (query) => api.query('archive', {source: {query: query, sort: ['_score'], size: 50}})
        .then((response) => {
            this.items = response._items;
        }, (reason) => {
            this.items = [];
        });

    search();

    // set given picture as featured for current item
    this.setFeatured = (picture) => {
        const associations = Object.assign({}, $scope.item.associations || {});

        associations.featuremedia = picture;
        $scope.item.associations = associations;

        $scope.autosave($scope.item);
    };

    // add picture to item photo gallery
    this.addToGallery = (picture) => {
        const associations = Object.assign({}, $scope.item.associations || {});
        const index = max(Object.keys(associations).map((key) => {
            if (key.indexOf(GALLERY) === 0) {
                return mediaIdGenerator.getFieldParts(key)[1] || 0;
            }

            return 0;
        }));

        const rel = mediaIdGenerator.getFieldVersionName(GALLERY, index + 1);

        associations[rel] = picture;
        $scope.item.associations = associations;

        $scope.autosave($scope.item);
    };

    this.allowAddMedia = () => $scope._editable && $scope.item.type === 'text';
}