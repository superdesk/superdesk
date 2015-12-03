describe('templates', function() {
    'use strict';

    beforeEach(module('superdesk.templates'));
    beforeEach(module('superdesk.templates-cache'));

    describe('templates widget', function() {

        var existingTemplate = {template_name: 'template1'};

        beforeEach(inject(function(desks, api, $q) {
            spyOn(desks, 'fetchCurrentUserDesks').and.returnValue($q.when({_items: []}));
            spyOn(api, 'save').and.returnValue($q.when({}));
            spyOn(api, 'find').and.returnValue($q.when(existingTemplate));
        }));

        it('should create a template', inject(function($controller, api, $q, $rootScope) {
            var item = _.create({slugline: 'FOO', headline: 'foo'});
            var ctrl = $controller('CreateTemplateController', {item: item});
            expect(ctrl.name).toBe('FOO');
            expect(ctrl.type).toBe('create');
            ctrl.name = 'test';
            ctrl.desk = 'news';
            ctrl.hasCrops = true;
            ctrl.save();
            expect(api.save).toHaveBeenCalledWith('content_templates', {
                template_name: 'test',
                template_type: 'create',
                template_desk: null,
                is_private: true,
                data: {
                    headline: 'foo',
                    slugline: 'FOO'
                }
            }, null);
        }));

        it('can update template', inject(function($controller, api, $q, $rootScope) {
            var item = _.create({slugline: 'FOO', template: '123'});
            var ctrl = $controller('CreateTemplateController', {item: item});
            $rootScope.$digest();
            expect(api.find).toHaveBeenCalledWith('content_templates', '123');
            expect(ctrl.name).toBe(existingTemplate.template_name);
            expect(ctrl.type).toBe('create');
            ctrl.save();
            expect(api.save.calls.argsFor(0)[1]).toBe(existingTemplate);
        }));
    });

    describe('templates service', function() {
        beforeEach(inject(function($q, api) {
            spyOn(api, 'query').and.returnValue($q.when());
        }));
        it('can fetch templates using default parameters', inject(function(api, templates) {
            templates.fetchTemplates();
            expect(api.query).toHaveBeenCalledWith('content_templates', {
                max_results: 10,
                page: 1
            });
        }));
        it('can fetch templates using page parameters', inject(function(api, templates) {
            templates.fetchTemplates(2, 25);
            expect(api.query).toHaveBeenCalledWith('content_templates', {
                max_results: 25,
                page: 2
            });
        }));
        it('can fetch templates using type parameter', inject(function(api, templates) {
            templates.fetchTemplates(undefined, undefined, 'create');
            expect(api.query).toHaveBeenCalledWith('content_templates', {
                max_results: 10,
                page: 1,
                where: '{"$and":[{"template_type":"create"}]}'
            });
        }));
        it('can fetch templates using desk parameter', inject(function(api, templates) {
            templates.fetchTemplates(undefined, undefined, undefined, 'desk1');
            expect(api.query).toHaveBeenCalledWith('content_templates', {
                max_results: 10,
                page: 1,
                where: '{"$and":[{"$or":[{"template_desk":"desk1","is_private":{"$ne":true}}]}]}'
            });
        }));
        it('can fetch templates using personal desk parameter', inject(function(api, templates) {
            templates.fetchTemplates(undefined, undefined, undefined, null, 'foo');
            expect(api.query).toHaveBeenCalledWith('content_templates', {
                max_results: 10,
                page: 1,
                where: '{"$and":[{"$or":[{"user":"foo","is_private":true}]}]}'
            });
        }));
        it('can fetch templates using keyword parameter', inject(function(api, templates) {
            templates.fetchTemplates(undefined, undefined, undefined, undefined, null, 'keyword');
            expect(api.query).toHaveBeenCalledWith('content_templates', {
                max_results: 10,
                page: 1,
                where: '{"$and":[{"template_name":{"$regex":"keyword","$options":"-i"}}]}'
            });
        }));
        it('can fetch templates by id', inject(function(api, templates) {
            templates.fetchTemplatesByIds([123, 456]);
            expect(api.query).toHaveBeenCalledWith('content_templates', {
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
            expect(api.query).toHaveBeenCalledWith('content_templates', {
                max_results: 10,
                page: 1,
                where: '{"_id":{"$in":["template2","template3"]}}'
            });
        }));
    });

    describe('template select directive', function() {
        it('can fetch desk templates and user private templates together',
        inject(function(api, session, desks, $rootScope, $compile, $q) {
            $rootScope.$digest(); // let it reset identity in auth
            session.identity = {_id: 'foo'};
            desks.activeDeskId = 'sports';
            spyOn(api, 'query').and.returnValue($q.when({_items: [
                {_id: 'public1'},
                {_id: 'public2'},
                {_id: 'private', is_private: true}
            ], _meta: {total: 3}}));
            var scope = $rootScope.$new();
            var elem = $compile('<div sd-template-select></div>')(scope);
            $rootScope.$digest();
            expect(api.query).toHaveBeenCalled();
            var args = api.query.calls.argsFor(0);
            expect(args[0]).toBe('content_templates');
            var where = JSON.parse(args[1].where);
            expect(where.$and.length).toBe(1);
            var $or = where.$and[0].$or;
            expect($or).toContain({is_private: {$ne: true}, template_desk: 'sports'});
            expect($or).toContain({is_private: true, user: session.identity._id});
            $rootScope.$digest();
            var iscope = elem.isolateScope();
            expect(iscope.publicTemplates.length).toBe(2);
            expect(iscope.privateTemplates.length).toBe(1);
        }));
    });
});
