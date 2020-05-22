import {isEmpty} from 'lodash';

// duplicated in extensions/imageShortcuts/src/get-widgets.tsx
// constants aren't used to avoid imports between multiple projects
const featureMediaField = 'feature_media';
const galleryField = 'photoGallery';

// only supporting Rome for the time being
const getQueryTimeZone = () => {
    const now = new Date();

    return now.getTimezoneOffset() === -120 ? '+02:00' : '+01:00';
};

AnsaRelatedCtrl.$inject = ['$scope', 'api', 'storage', 'Keys'];
export default function AnsaRelatedCtrl($scope, api, storage, Keys) {
    const search = () => {
        this.items = null;
        let semantics = $scope.item.semantics || {};

        if (isEmpty(semantics.iptcCodes) && isEmpty(semantics.persons)
            && isEmpty(semantics.organisations) && !this.query) {
            this.items = [];
            return;
        }

        let filters = [];
        let keys = ['persons', 'organizations'];
        let namespace = (key) => 'semantics.' + key;

        keys.forEach((key) => {
            if (semantics[key] && semantics[key].length) {
                semantics[key].forEach((val) => {
                    let f = {};

                    f[namespace(key)] = val;

                    if (key === 'persons') {
                        filters.push({match: {[namespace(key)]: {query: val, operator: 'and'}}});
                    } else {
                        filters.push({match_phrase: f});
                    }
                });
            }
        });

        let query = {
            bool: {
                must: [{term: {type: this.activeFilter}}],
                should: filters,
                must_not: [{term: {item_id: $scope.item._id}}],
                minimum_should_match: window.MINIMUM_SHOULD_MATCH || 1,
            },
        };

        if (!isEmpty(semantics.iptcCodes) && this.activeFilter === 'text') {
            query.bool.must.push({terms: {'semantics.iptcCodes': semantics.iptcCodes}});
        }

        if (this.query) {
            query = {
                bool: {
                    must: [
                        {term: {type: this.activeFilter}},
                        {query_string: {query: this.query, lenient: true, default_operator: 'AND'}},
                    ],
                    must_not: [{term: {item_id: $scope.item._id}}],
                },
            };
        }

        // filter out older versions
        query.bool.must.push(
            {term: {state: 'published'}}
        );

        // and rewritten versions
        query.bool.must_not.push(
            {exists: {field: 'rewritten_by'}}
        );

        // filter out afp
        query.bool.must_not.push({term: {creditline: 'AFP'}});

        // filter out used
        query.bool.must_not.push({range: {used_updated: {gte: 'now/d', time_zone: getQueryTimeZone()}}});

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

    this.apiQuery = (query) => api.query('news', {source: {
        query: query,
        sort: [{versioncreated: 'desc'}],
        size: 50,
    }})
        .then((response) => {
            this.items = response._items.map((published) => Object.assign(
                {_type: published.archive_item ? 'archive' : 'published'},
                published.archive_item || published
            ));
        }, (reason) => {
            this.items = [];
        });

    search();

    // set given picture as featured for current item
    this.setFeatured = (picture) => {
        window['__private_ansa__add_image_to_article'](featureMediaField, picture);
    };

    // add picture to item photo gallery
    this.addToGallery = (picture) => {
        window['__private_ansa__add_image_to_article'](galleryField, picture);
    };

    this.allowAddMedia = () => $scope._editable && $scope.item.type === 'text';

    $scope.featureMediaField = featureMediaField;
    $scope.galleryField = galleryField;

    $scope.$watch('item', (item) => {
        $scope.contentProfile = null;

        window['__private_ansa__get_content_profile'](item.profile).then((contentProfile) => {
            $scope.contentProfile = contentProfile;
        });
    });
}
