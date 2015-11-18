
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

    it('initializes the list of available field names in scope', function () {
        expect(scope.contentFields).toEqual([
            'body_text', 'guid', 'published_parsed',
            'summary', 'title', 'updated_parsed'
        ]);
    });

    it('initializes field aliases in scope to an empty list', function () {
        expect(scope.fieldAliases).toEqual([]);
    });

    it('initializes the list of field names without aliases to all ' +
       'content fields',
        function () {
            expect(scope.fieldsNotSelected).toEqual([
                'body_text', 'guid', 'published_parsed',
                'summary', 'title', 'updated_parsed'
            ]);
        }
    );

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

    describe('edit() method', function () {
        var fakeProvider;

        beforeEach(function () {
            fakeProvider = {
                config: {
                    field_aliases: [
                        {foo2: 'bar2'},
                        {foo5: 'bar5'}
                    ]
                }
            };
            scope.contentFields = ['foo', 'foo2', 'foo3', 'foo4', 'foo5'];
        });

        it('updates the list of field name aliases to match ' +
           'provider\'s configuration',
            function () {
                scope.fieldAliases = [{fieldName: 'body', alias: 'content'}];
                scope.edit(fakeProvider);
                expect(scope.fieldAliases).toEqual([
                    {fieldName: 'foo2', alias: 'bar2'},
                    {fieldName: 'foo5', alias: 'bar5'}
                ]);
            }
        );

        it('updates the list of field names that don\'t have an alias set',
            function () {
                scope.fieldsNotSelected = [];
                scope.edit(fakeProvider);
                expect(scope.fieldsNotSelected).toEqual(
                    ['foo', 'foo3', 'foo4']
                );
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
        beforeEach(function () {
            scope.fieldAliases = [
                {fieldName: 'foo', alias: 'bar'},
                {fieldName: 'foo2', alias: 'bar2'},
                {fieldName: 'foo3', alias: 'bar3'}
            ];
        });

        it('removes an item at given index from the list of field aliases',
            function () {
                scope.removeFieldAlias(1);
                expect(scope.fieldAliases).toEqual([
                    {fieldName: 'foo', alias: 'bar'},
                    {fieldName: 'foo3', alias: 'bar3'}
                 ]);
            }
        );

        it('adds removed items\'s selected field name to the list of ' +
           'not selected fields',
            function () {
                scope.fieldsNotSelected = ['field_x'];
                scope.removeFieldAlias(1);
                expect(scope.fieldsNotSelected).toEqual(['field_x', 'foo2']);
            }
        );

        it('does not modify the list of not selected fields if removed ' +
           'alias item did not have a field name selected',
            function () {
                scope.fieldsNotSelected = ['field_x'];
                scope.fieldAliases[1].fieldName = null;

                scope.removeFieldAlias(1);

                expect(scope.fieldsNotSelected).toEqual(['field_x']);
            }
        );
    });

    describe('fieldSelectionChanged() method', function () {
        beforeEach(function () {
            scope.contentFields = ['field_1', 'field_2', 'field_3', 'field_4'];
        });

        it('updates the list of fields not selected', function () {
            scope.fieldsNotSelected = ['field_2'];

            // let's say an alias for field_3 gets removed:
            scope.fieldAliases = [
                {fieldName: 'field_1', alias: 'alias_1'},
                {fieldName: 'field_4', alias: 'alias_4'},
                {fieldName: null, alias: 'whatever'}
            ];
            scope.fieldSelectionChanged();

            expect(scope.fieldsNotSelected).toEqual(['field_2', 'field_3']);
        });
    });

    describe('availableFieldOptions() method', function () {
        beforeEach(function () {
            scope.contentFields = ['field_1', 'field_2', 'field_3', 'field_4'];
            scope.fieldsNotSelected = ['field_1', 'field_3'];
        });

        it('returns only the field names currently not selected if no field ' +
           'name is given',
            function () {
                var fieldNames = scope.availableFieldOptions(null);
                expect(fieldNames).toEqual(['field_1', 'field_3']);
            }
        );

        it('returns field names currently not selected ' +
           'plus the given field name',
            function () {
                var fieldNames = scope.availableFieldOptions('field_4');
                expect(fieldNames).toEqual(['field_1', 'field_3', 'field_4']);
            }
        );
    });

    describe('save() method', function () {
        var deferredSave;

        beforeEach(inject(function ($q, api) {
            deferredSave = $q.defer();

            api.ingestProviders = {
                save: jasmine.createSpy().and.returnValue(deferredSave.promise)
            };

            scope.provider = {
                config: {
                    field_aliases: [{headline: 'title'}]
                }
            };
        }));

        it('updates field aliases in provider configuration', function () {
            scope.fieldAliases = [
                {fieldName: 'foo', alias: 'bar'},
                {fieldName: 'foo2', alias: 'bar2'}
            ];
            scope.save();
            expect(scope.provider.config.field_aliases).toEqual(
                [{foo: 'bar'}, {foo2: 'bar2'}]
            );
        });

        it('does not add field aliases with missing data to ' +
           ' provider configuration',
           function () {
                scope.fieldAliases = [
                    {fieldName: 'headline', alias: ''},
                    {fieldName: null, alias: 'some_alias'},
                    {fieldName: null, alias: ''}
                ];
                scope.save();
                expect(scope.provider.config.field_aliases).toEqual([]);
            }
        );
    });

});
