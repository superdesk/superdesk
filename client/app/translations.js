angular.module('gettext').run(['gettextCatalog', function (gettextCatalog) {
/* jshint -W100 */
    gettextCatalog.setStrings('de', {"My Profile":"DE - My Profile"});
    gettextCatalog.setStrings('en', {
        "SUBJECT":"TOPIC",
        "Subject": "Topic",
        "SLUGLINE": "KEYWORD",
        "Slugline": "Keyword",
        "KEYWORDS": "TAGS",
        "Keywords": "Tags"
    });
/* jshint +W100 */
}]);