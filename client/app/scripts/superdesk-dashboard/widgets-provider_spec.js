'use strict';

describe('widgets provider', function() {

    beforeEach(module('superdesk.dashboard.widgets'));

    /*
    beforeEach(module(function($provide) {
        var provider = $provide.provider('widgets', WidgetsProvider);
        provider.widget('id', {label: 'first'});
        provider.widget('id', {label: 'second'});
    }));
    */

    beforeEach(inject(function (_widgets_) { 
        widgets = _widgets_;
        widgets.widget('id', {label: 'first'});
        widgets.widget('id', {label: 'second'});
    } 

    it('is defined', function() {
        expect(WidgetsProvider).not.toBe(undefined);
    });

    //it('can register widgets', inject(function(widgets) {
    it('can register widgets', function() {
        expect(widgets.length).toBe(1);
        expect(widgets[0]._id).toBe('id');
        expect(widgets[0].label).toBe('second');
    }));
});
