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
});
