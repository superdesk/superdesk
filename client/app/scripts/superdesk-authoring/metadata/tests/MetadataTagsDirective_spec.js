'use strict';

describe('MetadataTags directive', function () {
    var scope, element, apiEndpoint, apiData;

    var bodyHtml = '<div x="1"><span y="2">realBody</span></div>';

    beforeEach(module('templates'));
    beforeEach(module('superdesk.authoring.metadata'));
    beforeEach(module(function($provide) {
        $provide.service('api', function($q) {
            return {
                save: function(endpoint, data) {
                    apiEndpoint = endpoint;
                    apiData = data;
                    return $q.when({keywords: [{text: 'foo'}, {text: 'bar'}]});
                }
            };
        });
    }));

    beforeEach(inject(function ($rootScope, $compile, api) {
        scope = $rootScope.$new();
        element = angular.element([
            '<div sd-meta-tags data-item="item" data-field="keywords"',
            'data-source-field="body_html" data-change="autosave(item)"',
            'data-disabled="!_editable">'
        ].join(' '));
        scope.item = {body_html: bodyHtml, keywords: ['baz']};
        element = $compile(element)(scope);
        scope.$digest();
    }));

    it('can strip html and query for keywords', function() {
        expect(apiEndpoint).toBe('keywords');
        expect(apiData).toEqual({text: 'realBody'});
    });

    it('can update tags', function() {
        expect(element.isolateScope().extractedTags).toEqual(['foo', 'bar']);
        expect(element.isolateScope().tags).toEqual(['foo', 'bar', 'baz']);
    });
});
