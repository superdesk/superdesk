'use strict';

describe('item comments', function() {

    beforeEach(module(function($provide) {
        $provide.provider('api', function() {
            this.api = function() {};
            this.$get = function() {
                return {
                    item_comments: {
                        query: function() {
                            return;
                        }
                    }
                };
            };
        });
    }));

    beforeEach(module('superdesk.authoring.comments'));

    it('can fetch comments for an item', inject(function(commentsService, api, $rootScope, $q) {

        spyOn(api.item_comments, 'query').and.returnValue($q.when({_items: [{_id: 1}]}));

        commentsService.fetch('test-id').then(function() {
            expect(commentsService.comments.length).toBe(1);
        });

        $rootScope.$apply();

        expect(api.item_comments.query).toHaveBeenCalledWith({
            where: {item: 'test-id'}, embedded: {user: 1}
        });
    }));
});
