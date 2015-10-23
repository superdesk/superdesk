
var route = require('./helpers/utils').route,
    monitoring = require('./helpers/monitoring'),
    search = require('./helpers/search'),
    authoring = require('./helpers/authoring'),
    workspace = require('./helpers/workspace'),
    highlights = require('./helpers/highlights');

describe('HIGHLIGHTS', function() {
    'use strict';

    describe('add highlights configuration:', function() {
        beforeEach(route('/settings/highlights'));

        it('highlights management', function() {
            //add highlights configuration with one desk
            highlights.add();
            highlights.setName('highlight new');
            highlights.setTemplate('custom_highlight');
            highlights.toggleDesk('Sports Desk');
            highlights.save();
            expect(highlights.getRow('highlight new').count()).toBe(1);
            highlights.edit('highlight new');
            expect(highlights.getTemplate()).toMatch('custom_highlight');
            highlights.expectDeskSelection('Sports Desk', true);
            highlights.cancel();

            //add highlights configuration with the same name'
            highlights.add();
            highlights.setName('Highlight one');
            highlights.save();
            highlights.cancel();
            expect(highlights.getRow('Highlight one').count()).toBe(1);

            //add highlights configuration with no desk
            highlights.add();
            highlights.setName('highlight no desk');
            highlights.save();
            expect(highlights.getRow('highlight no desk').count()).toBe(1);

            //add highlights configuration with no group
            highlights.add();
            highlights.setName('highlight no group');
            highlights.save();
            highlights.edit('highlight no group');
            expect(highlights.groups.count()).toBe(1);
            expect(highlights.getGroup('main').count()).toBe(1);
            highlights.cancel();

            //add highlights configuration with group first
            highlights.add();
            highlights.setName('highlight first group');
            highlights.addGroup('first');
            highlights.save();
            highlights.edit('highlight first group');
            expect(highlights.groups.count()).toBe(1);
            expect(highlights.getGroup('first').count()).toBe(1);
            highlights.cancel();

            //set default template for highlight configuration
            highlights.edit('highlight one');
            highlights.setTemplate('default');
            highlights.save();
            highlights.edit('highlight one');
            expect(highlights.getTemplate()).toMatch('');
            highlights.cancel();

            //change the name of highlight configuration
            highlights.edit('highlight one');
            highlights.setName('highlight new name');
            highlights.save();
            expect(highlights.getRow('highlight new name').count()).toBe(1);
            expect(highlights.getRow('highlight one').count()).toBe(0);

            //add a desk to highlight configuration
            highlights.edit('highlight new name');
            highlights.expectDeskSelection('Politic Desk', false);
            highlights.toggleDesk('Politic Desk');
            highlights.save();
            highlights.edit('highlight new name');
            highlights.expectDeskSelection('Politic Desk', true);
            highlights.cancel();

            //delete a desk from highlight configuration
            highlights.edit('highlight three');
            highlights.expectDeskSelection('Politic Desk', true);
            highlights.toggleDesk('Politic Desk');
            highlights.save();
            highlights.edit('highlight three');
            highlights.expectDeskSelection('Politic Desk', false);
            highlights.cancel();

            //add a group to highlight configuration
            highlights.edit('highlight three');
            expect(highlights.groups.count()).toBe(1);
            expect(highlights.getGroup('main').count()).toBe(1);
            highlights.addGroup('last');
            highlights.save();
            highlights.edit('highlight three');
            expect(highlights.groups.count()).toBe(2);
            expect(highlights.getGroup('main').count()).toBe(1);
            expect(highlights.getGroup('last').count()).toBe(1);
            highlights.cancel();

            //edit group from highlight configuration
            highlights.edit('highlight four');
            expect(highlights.groups.count()).toBe(1);
            expect(highlights.getGroup('main').count()).toBe(1);
            highlights.editGroup('main', 'first');
            highlights.save();
            highlights.edit('highlight four');
            expect(highlights.groups.count()).toBe(1);
            expect(highlights.getGroup('first').count()).toBe(1);
            highlights.cancel();

            //delete the single group from highlight configuration
            highlights.edit('highlight four');
            expect(highlights.groups.count()).toBe(1);
            expect(highlights.getGroup('first').count()).toBe(1);
            highlights.deleteGroup('first');
            highlights.save();
            highlights.edit('highlight four');
            expect(highlights.groups.count()).toBe(1);
            expect(highlights.getGroup('main').count()).toBe(1);
            highlights.cancel();

            //delete one group from highlight configuration
            highlights.edit('highlight three');
            expect(highlights.groups.count()).toBe(2);
            expect(highlights.getGroup('main').count()).toBe(1);
            expect(highlights.getGroup('last').count()).toBe(1);
            highlights.deleteGroup('main');
            highlights.save();
            highlights.edit('highlight three');
            expect(highlights.groups.count()).toBe(1);
            expect(highlights.getGroup('last').count()).toBe(1);
            highlights.cancel();

            //delete highlight configuration'
            expect(highlights.getRow('highlight four').count()).toBe(1);
            highlights.remove('highlight four');
            expect(highlights.getRow('highlight four').count()).toBe(0);
        });
    });

    describe('mark for highlights in a desk:', function() {
        beforeEach(route('/workspace/monitoring'));

        it('create highlight package', function() {
            //mark for highlight in monitoring
            monitoring.actionOnItemSubmenu('Mark for highlight', 'Highlight two', 1, 0);
            monitoring.actionOnItemSubmenu('Mark for highlight', 'Highlight three', 1, 2);
            monitoring.checkMarkedForHighlight('Highlight two', 1, 0);
            monitoring.checkMarkedForHighlight('Highlight three', 1, 2);

            //mark for highlight in authoring
            monitoring.actionOnItem('Edit', 1, 1);
            authoring.markForHighlights();
            expect(highlights.getHighlights(authoring.getSubnav()).count()).toBe(3);
            highlights.selectHighlight(authoring.getSubnav(), 'Highlight two');
            authoring.checkMarkedForHighlight('Highlight two');
            search.openGlobalSearch();
            monitoring.openMonitoring();
            monitoring.checkMarkedForHighlight('Highlight two', 1, 1);

            //multi mark for highlights
            monitoring.selectItem(1, 3);
            monitoring.selectItem(2, 0);
            highlights.multiMarkHighlight('Highlight two');
            monitoring.checkMarkedForHighlight('Highlight two', 1, 3);
            monitoring.checkMarkedForHighlight('Highlight two', 2, 0);

            //multi mark for highlights, in case of partial mark for selected items
            monitoring.selectItem(2, 0);
            monitoring.selectItem(2, 1);
            highlights.multiMarkHighlight('Highlight two');
            monitoring.checkMarkedForHighlight('Highlight two', 2, 0);
            monitoring.checkMarkedForHighlight('Highlight two', 2, 1);

            //create the highlight and add a item to it
            highlights.createHighlightsPackage('Highlight two');
            workspace.actionOnItemSubmenu('Add to current', 'main', 3);
            expect(authoring.getGroupItems('main').count()).toBe(1);

            //from monitoring add an item to highlight package
            workspace.showList('Monitoring');
            monitoring.actionOnItemSubmenu('Add to current', 'story', 2, 2);
            expect(authoring.getGroupItems('story').count()).toBe(1);

            //show highlist three and add an item to highlight package
            workspace.showHighlightList('Highlight three');
            workspace.actionOnItemSubmenu('Add to current', 'sidebars', 0);
            expect(authoring.getGroupItems('sidebars').count()).toBe(1);

            //export highlight
            authoring.save();
            highlights.exportHighlights();

            //check that the new highlight package and generated list are on personal
            workspace.showList('Personal');
            expect(workspace.getItemText(0)).toBe('Highlight two');
            expect(workspace.getItemText(1)).toBe('Highlight two');
        });
    });
});
