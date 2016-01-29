angular.module('gettext').run(['gettextCatalog', function (gettextCatalog) {
    gettextCatalog.setStrings('de', {"My Profile":"DE - My Profile"});
}]);
