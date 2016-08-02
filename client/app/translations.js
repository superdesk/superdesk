angular.module('gettext').run(['gettextCatalog', function (gettextCatalog) {
    gettextCatalog.setStrings('en', {
        "URGENCY": "NEWS VALUE",
        "Urgency": "News Value",
        "urgency": "news value",
        "Urgency stats": "News Value stats",
        "SERVICE": "CATEGORY",
        "Mar": "March",
        "Apr": "April",
        "Jun": "June",
        "Jul": "July",
        "Sep": "Sept"        
    });
}]);
