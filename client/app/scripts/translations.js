angular.module('gettext').run(['gettextCatalog', function (gettextCatalog) {
/* jshint -W100 */
    gettextCatalog.setStrings('cs', {"Please authenticate to continue":"Prosím přihlašte se","Login failed!":"Nepodařilo se přihlásit","Login session expired!":"Vypršel login","Remember login":"Zapamatuj si mě","Submit":"Odeslat","Username":"Uživatel","Password":"Heslo"});
/* jshint +W100 */
}]);