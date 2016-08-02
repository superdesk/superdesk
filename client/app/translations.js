angular.module('gettext').run(['gettextCatalog', function (gettextCatalog) {
/* jshint -W100 */
    gettextCatalog.setStrings('de', {"My Profile":"DE - My Profile"});
    gettextCatalog.setStrings('en', {});
/* jshint +W100 */
}]);