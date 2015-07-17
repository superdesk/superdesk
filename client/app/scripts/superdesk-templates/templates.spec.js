describe('templates', function() {
    'use strict';

    beforeEach(module('superdesk.templates'));

    describe('templates widget', function() {
        it('should create a template', inject(function($controller, api, desks, $q, $rootScope) {
            spyOn(desks, 'fetchCurrentUserDesks').and.returnValue($q.when({_items: []}));
            spyOn(api, 'save').and.returnValue($q.when({}));

            var item = _.create({slugline: 'FOO', headline: 'foo'}),
                ctrl = $controller('CreateTemplateController', {item: item});
            expect(ctrl.name).toBe('FOO');
            expect(ctrl.type).toBe('create');
            ctrl.name = 'test';
            ctrl.desk = 'news';
            ctrl.save();
            expect(api.save).toHaveBeenCalledWith('content_templates', {
                template_name: 'test',
                template_type: 'create',
                template_desk: 'news',
                headline: 'foo',
                slugline: 'FOO'
            });
        }));
    });

    describe('templates service', function() {
        beforeEach(inject(function($q, api) {
            spyOn(api.content_templates, 'query').and.returnValue($q.when());
        }));
        it('can fetch templates using default parameters', inject(function(api, templates) {
            templates.fetchTemplates();
            expect(api.content_templates.query).toHaveBeenCalledWith({
                max_results: 10,
                page: 1
            });
        }));
        it('can fetch templates using page parameters', inject(function(api, templates) {
            templates.fetchTemplates(2, 25);
            expect(api.content_templates.query).toHaveBeenCalledWith({
                max_results: 25,
                page: 2
            });
        }));
        it('can fetch templates using type parameter', inject(function(api, templates) {
            templates.fetchTemplates(undefined, undefined, 'create');
            expect(api.content_templates.query).toHaveBeenCalledWith({
                max_results: 10,
                page: 1,
                where: '{"$and":[{"template_type":"create"}]}'
            });
        }));
        it('can fetch templates using desk parameter', inject(function(api, templates) {
            templates.fetchTemplates(undefined, undefined, undefined, 'desk1');
            expect(api.content_templates.query).toHaveBeenCalledWith({
                max_results: 10,
                page: 1,
                where: '{"$and":[{"template_desk":"desk1"}]}'
            });
        }));
        it('can fetch templates using personal desk parameter', inject(function(api, templates) {
            templates.fetchTemplates(undefined, undefined, undefined, null);
            expect(api.content_templates.query).toHaveBeenCalledWith({
                max_results: 10,
                page: 1,
                where: '{"$and":[{"template_desk":null}]}'
            });
        }));
        it('can fetch templates using keyword parameter', inject(function(api, templates) {
            templates.fetchTemplates(undefined, undefined, undefined, undefined, 'keyword');
            expect(api.content_templates.query).toHaveBeenCalledWith({
                max_results: 10,
                page: 1,
                where: '{"$and":[{"template_name":{"$regex":"keyword","$options":"-i"}}]}'
            });
        }));
        it('can fetch templates using all parameters', inject(function(api, templates) {
            templates.fetchTemplates(25, 2, 'create', 'desk1', 'keyword');
            expect(api.content_templates.query).toHaveBeenCalledWith({
                max_results: 2,
                page: 25,
                where: angular.toJson({$and: [{
                    template_type: 'create',
                    template_desk: 'desk1',
                    template_name: {$regex: 'keyword', $options: '-i'}
                }]})
            });
        }));
        it('can fetch templates by id', inject(function(api, templates) {
            templates.fetchTemplatesByIds([123, 456]);
            expect(api.content_templates.query).toHaveBeenCalledWith({
                max_results: 10,
                page: 1,
                where: '{"_id":{"$in":[123,456]}}'
            });
        }));
        it('can add recent templates', inject(function(api, templates, preferencesService, $q, $rootScope) {
            spyOn(preferencesService, 'get').and.returnValue($q.when({}));
            spyOn(preferencesService, 'update').and.returnValue($q.when());
            templates.addRecentTemplate('desk1', 'template1');
            $rootScope.$digest();
            expect(preferencesService.update).toHaveBeenCalledWith({
                'templates:recent': {
                    'desk1': ['template1']
                }
            });
        }));
        it('can get recent templates', inject(function(api, templates, preferencesService, $q, $rootScope) {
            spyOn(preferencesService, 'get').and.returnValue($q.when({
                'templates:recent': {
                    'desk2': ['template2', 'template3']
                }
            }));
            templates.getRecentTemplates('desk2');
            $rootScope.$digest();
            expect(api.content_templates.query).toHaveBeenCalledWith({
                max_results: 10,
                page: 1,
                where: '{"_id":{"$in":["template2","template3"]}}'
            });
        }));
    });
});
