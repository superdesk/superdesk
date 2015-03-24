
/**
* Module with tests for the sdIngestSourcesContent directive
*
* @module sdIngestSourcesContent directive tests
*/
describe('sdIngestSourcesContent directive', function () {
    'use strict';

    var scope;

    beforeEach(module('superdesk.ingest'));

    beforeEach(inject(function ($compile, $rootScope, $templateCache) {
        var html,
            templateUrl;

        templateUrl = [
            'scripts', 'superdesk-ingest', 'views',
            'settings', 'ingest-sources-content.html'
        ].join('/');

        // since the directive does not modify the DOM, we can just
        // give it any kind of template
        $templateCache.put(templateUrl, '<div>whatever</div>');

        scope = $rootScope.$new();
        html = '<div sd-ingest-sources-content></div>';
        $compile(html)(scope);
        scope.$digest();
    }));

    it('some dummy first test', function () {
        console.debug(scope.minutes);
        expect(scope.minutes).toBeDefined();  // this works now! just fix tpl cache issue
       //  debugger;
    });

    // TODO: scope.save() ... check that aliases are in config!

});
