angular.module('gettext').run(['gettextCatalog', function (gettextCatalog) {
    gettextCatalog.setStrings('en', {
        "URGENCY": "NEWS VALUE",
        "Urgency": "News Value",
        "urgency": "news value",
        "Urgency stats": "News Value stats",
        "SERVICE": "CATEGORY",
        "SERVICES": "CATEGORIES",
        "Services": "Categories",
        "Mar": "March",
        "Apr": "April",
        "Jun": "June",
        "Jul": "July",
        "Sep": "Sept"        
    });
}]);
