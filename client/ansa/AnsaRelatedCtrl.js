import {max, get, isEmpty} from 'lodash';

// must match gallery field id
const GALLERY = 'photoGallery';

AnsaRelatedCtrl.$inject = ['$scope', 'api', 'storage', 'Keys', 'mediaIdGenerator'];
export default function AnsaRelatedCtrl($scope, api, storage, Keys, mediaIdGenerator) {
    const search = () => {
        if (isEmpty(get($scope.item, 'semantics.iptcCodes')) && !this.query) {
            this.items = [];
            return;
        }

        this.items = null;

        let filters = [];
        let semantics = $scope.item.semantics || {};
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

        let query = {
            bool: {
                must_not: [{term: {item_id: $scope.item._id}}],
                should: [],
            },
        };

        angular.extend(query.bool, {
            must: [
                {term: {type: 'text'}},
                {terms: {'semantics.iptcCodes': semantics.iptcCodes}},
            ],
            should: filters,
            minimum_should_match: 1,
        });

        if (this.query) {
            query = {
                bool: {
                    must: [
                        {term: {type: this.activeFilter}},
                        {query_string: {query: this.query, lenient: true}},
                    ],
                    must_not: [{term: {item_id: $scope.item._id}}],
                },
            };
        }

        // filter out older versions
        query.bool.must.push(
            {term: {last_published_version: true}}
        );

        // and rewritten versions
        query.bool.must_not.push(
            {exists: {field: 'rewritten_by'}}
        );

        console.info('query', angular.toJson(query, 2));

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

    this.apiQuery = (query) => api.query('published', {source: {
        query: query,
        sort: ['_score', {versioncreated: 'desc'}],
        size: 50,
    }})
        .then((response) => {
            this.items = response._items.map((published) => published.archive_item || published);
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