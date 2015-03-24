
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

    it('initializes field aliases in scope to a list containing a single ' +
       'empty alias item',
       function () {
            expect(scope.fieldAliases).toEqual([
                {fieldName: null, alias: ''}
            ]);
        }
    );

    it('initializes the list of available field names in scope', function () {
        expect(scope.contentFields).toEqual([
            'body_text', 'guid', 'published_parsed',
            'summary', 'title', 'updated_parsed'
        ]);
    });

    describe('setRssConfig() method', function () {
        var fakeProvider;

        beforeEach(function () {
            scope.provider = {
                config: {}
            };
            fakeProvider = {
                config: {
                    auth_required: true,
                    username: 'user',
                    password: 'password'
                }
            };
        });

        it('stores provider configuration in scope', function () {
            scope.setRssConfig(fakeProvider);
            expect(scope.provider.config).toEqual({
                auth_required: true, username: 'user', password: 'password'
            });
        });

        it('removes username and password from provider config if ' +
           'authenticationration is not required',
           function () {
                fakeProvider.config.auth_required = false;
                scope.setRssConfig(fakeProvider);
                expect(scope.provider.config).toEqual({
                    auth_required: false, username: null, password: null
                });
            }
        );
    });

    describe('addFieldAlias() method', function () {
        it('appends a new item to the list of field aliases', function () {
            scope.fieldAliases = [
                {fieldName: 'foo', alias: 'bar'},
                {fieldName: 'foo2', alias: 'bar2'}
            ];

            scope.addFieldAlias();

            expect(scope.fieldAliases).toEqual([
                {fieldName: 'foo', alias: 'bar'},
                {fieldName: 'foo2', alias: 'bar2'},
                {fieldName: null, alias: ''}
             ]);
        });
    });

    describe('removeFieldAlias() method', function () {
        it('removes an item at given index from the list of field aliases',
            function () {
                scope.fieldAliases = [
                    {fieldName: 'foo', alias: 'bar'},
                    {fieldName: 'foo2', alias: 'bar2'},
                    {fieldName: 'foo3', alias: 'bar3'}
                ];

                scope.removeFieldAlias(1);

                expect(scope.fieldAliases).toEqual([
                    {fieldName: 'foo', alias: 'bar'},
                    {fieldName: 'foo3', alias: 'bar3'}
                 ]);
            }
        );
    });

    // TODO: scope.save() ... check that aliases are in config!

});
