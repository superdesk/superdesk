/**
 * This file is part of Superdesk.
 *
 * Copyright 2013, 2014 Sourcefabric z.u. and contributors.
 *
 * For the full copyright and license information, please see the
 * AUTHORS and LICENSE files distributed with this source code, or
 * at https://www.sourcefabric.org/superdesk/license
 */
'use strict';
var desks = require('./helpers/desks');

describe('desk maintenance', function() {

    beforeEach(function() {
        desks.openDesksSettings();
    });

    it('edit desk', function() {
        desks.edit('Politic Desk');
        desks.deskDescriptionElement().sendKeys('New Description');
        desks.deskSourceElement().sendKeys('Test');
        desks.setDeskType('production');
        desks.getNextButtonOnGeneralTab().click();
        desks.showTab('macros');
        desks.save();
        desks.edit('Politic Desk');
        expect(desks.deskDescriptionElement().getAttribute('value')).toEqual('New Description');
        expect(desks.deskSourceElement().getAttribute('value')).toEqual('Test');
        expect(desks.getDeskType().getAttribute('value')).toEqual('string:production');
    });

    it('add desk', function() {
        desks.getNewDeskButton().click();
        desks.deskNameElement().sendKeys('Test Desk');
        desks.deskDescriptionElement().sendKeys('Test Description');
        desks.deskSourceElement().sendKeys('Test Source');
        desks.setDeskType('authoring');
        desks.getNextButtonOnGeneralTab().click();
        desks.showTab('macros');
        desks.save();
        desks.edit('Test Desk');
        expect(desks.deskNameElement().getAttribute('value')).toEqual('Test Desk');
        expect(desks.deskDescriptionElement().getAttribute('value')).toEqual('Test Description');
        expect(desks.deskSourceElement().getAttribute('value')).toEqual('Test Source');
        expect(desks.getDeskType().getAttribute('value')).toEqual('string:authoring');
    });
});
