
var openUrl = require('./helpers/utils').open,
    workspace = require('./helpers/workspace'),
    content = require('./helpers/content'),
    authoring = require('./helpers/authoring'),
    highlights = require('./helpers/highlights');

describe('HIGHLIGHTS', function() {
    'use strict';

    describe('add highlights configuration:', function() {
        beforeEach(function() {
            openUrl('/#/settings/highlights');
        });

        it('add highlights configuration with one desk', function() {
            highlights.add();
            highlights.setName('highlight new');
            highlights.toggleDesk('Sports Desk');
            highlights.save();
            expect(highlights.getRow('highlight new').count()).toBe(1);
            highlights.edit('highlight new');
            highlights.expectDeskSelection('Sports Desk', true);
        });

        it('add highlights configuration with the same name', function() {
            highlights.add();
            highlights.setName('Highlight one');
            highlights.save();
            highlights.cancel();
            expect(highlights.getRow('Highlight one').count()).toBe(1);
        });

        it('add highlights configuration with no desk', function() {
            highlights.add();
            highlights.setName('highlight new');
            highlights.save();
            expect(highlights.getRow('highlight new').count()).toBe(1);
        });
    });

    describe('edit highlights configuration:', function() {
        beforeEach(function() {
            openUrl('/#/settings/highlights');
        });

        it('change the name of highlight configuration', function() {
            highlights.edit('highlight one');
            highlights.setName('highlight new');
            highlights.save();
            expect(highlights.getRow('highlight new').count()).toBe(1);
            expect(highlights.getRow('highlight one').count()).toBe(0);
        });

        it('add a desk to highlight configuration', function() {
            highlights.edit('highlight one');
            highlights.toggleDesk('Politic Desk');
            highlights.save();
            highlights.edit('highlight one');
            highlights.expectDeskSelection('Politic Desk', true);
        });

        it('delete a desk from highlight configuration', function() {
            highlights.edit('highlight one');
            highlights.toggleDesk('Sports Desk');
            highlights.save();
            highlights.edit('highlight one');
            highlights.expectDeskSelection('Sports Desk', false);
        });
    });

    describe('delete highlights configuration:', function() {
        beforeEach(function() {
            openUrl('/#/settings/highlights');
        });

        it('delete highlight configuration', function() {
            expect(highlights.getRow('highlight one').count()).toBe(1);
            highlights.remove('highlight one');
            expect(highlights.getRow('highlight one').count()).toBe(0);
        });
    });

    describe('mark for highlights in a desk:', function() {
        beforeEach(function() {
            openUrl('/#/workspace/content');
        });

        it('mark for highlights in list view', function() {
            workspace.switchToDesk('SPORTS DESK');
            content.setListView();
            content.actionOnItem('Mark item', 0);
            expect(highlights.getHighlights(content.getItem(0)).count()).toBe(2);
            highlights.selectHighlight(content.getItem(0), 'Highlight one');
            workspace.switchToDesk('PERSONAL');
            workspace.switchToDesk('SPORTS DESK');
            content.setListView();
            content.checkMarkedForHighlight('Highlight one', 0);
        });

        it('mark for highlights in edit article screen', function() {
            workspace.switchToDesk('SPORTS DESK');
            content.setListView();
            content.actionOnItem('Edit item', 0);
            authoring.markForHighlights();
            expect(highlights.getHighlights(authoring.getSubnav()).count()).toBe(2);
            highlights.selectHighlight(authoring.getSubnav(), 'Highlight one');
            authoring.checkMarkedForHighlight('Highlight one');
            authoring.close();
            workspace.switchToDesk('PERSONAL');
            workspace.switchToDesk('SPORTS DESK');
            content.setListView();
            content.checkMarkedForHighlight('Highlight one', 0);
        });

        it('create highlight package', function() {
            workspace.switchToDesk('PERSONAL');
            expect(content.getCount()).toBe(3);
            workspace.switchToDesk('SPORTS DESK');
            content.setListView();
            content.actionOnItem('Mark item', 0);
            highlights.selectHighlight(content.getItem(0), 'Highlight one');
            highlights.createHighlightsPackage('HIGHLIGHT ONE');
            authoring.showSearch();
            authoring.addToGroup(0, 'MAIN');
            authoring.save();
            authoring.close();
            workspace.switchToDesk('PERSONAL');
            expect(content.getCount()).toBe(4);
        });

        it('filter by highlights in highlight package', function() {
            workspace.switchToDesk('SPORTS DESK');
            content.setListView();
            content.actionOnItem('Mark item', 0);
            highlights.selectHighlight(content.getItem(0), 'Highlight one');

            workspace.switchToDesk('PERSONAL');
            workspace.switchToDesk('SPORTS DESK');
            content.setListView();
            content.actionOnItem('Mark item', 1);
            highlights.selectHighlight(content.getItem(1), 'Highlight one');

            workspace.switchToDesk('PERSONAL');
            workspace.switchToDesk('SPORTS DESK');
            content.setListView();
            content.actionOnItem('Mark item', 1);
            highlights.selectHighlight(content.getItem(1), 'Highlight two');

            highlights.createHighlightsPackage('HIGHLIGHT ONE');
            authoring.showSearch();
            expect(authoring.getSearchItemCount()).toBe(2);

            highlights.switchHighlightFilter('Highlight Two');
            expect(authoring.getSearchItemCount()).toBe(1);
        });

        it('export highlight package', function() {
            workspace.switchToDesk('SPORTS DESK');
            content.setListView();
            content.actionOnItem('Mark item', 0);
            highlights.selectHighlight(content.getItem(0), 'Highlight one');

            workspace.switchToDesk('PERSONAL');
            content.setListView();
            expect(content.getCount()).toBe(3);
            workspace.switchToDesk('SPORTS DESK');
            content.setListView();
            content.actionOnItem('Mark item', 1);
            highlights.selectHighlight(content.getItem(1), 'Highlight one');

            highlights.createHighlightsPackage('HIGHLIGHT ONE');
            authoring.showSearch();
            expect(authoring.getSearchItemCount()).toBe(2);

            authoring.addToGroup(0, 'MAIN');
            authoring.addToGroup(1, 'STORY');
            authoring.save();
            highlights.exportHighlights();
            authoring.save();
            authoring.close();

            workspace.switchToDesk('PERSONAL');
            content.setListView();
            expect(content.getCount()).toBe(5);
        });
    });
});
