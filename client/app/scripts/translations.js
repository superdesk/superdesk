angular.module('gettext').run(['gettextCatalog', function (gettextCatalog) {
/* jshint -W100 */
    gettextCatalog.setStrings('en', {
        "CATEGORY":"SERVICE",
        "Category": "Service",
        "SLUGLINE": "KEYWORD",
        "Slugline": "Keyword",
        "KEYWORDS": "TAGS",
        "Keywords": "Tags"
    });
/* jshint +W100 */
}]);