define([
    './workflowService'
], function(workflowServiceSpec) {
    'use strict';

    describe('Workflow Service', function() {

        beforeEach(module(workflowServiceSpec.name));

        beforeEach(inject(function(preferencesService, $q, workflowService) {
            var actions = [
                {
                    name: 'spike',
                    exclude_states: ['spiked', 'published', 'killed'],
                    privileges: ['spike']
                },
                {
                    name: 'fetch_as_from_ingest',
                    include_states: ['ingested'],
                    privileges: ['ingest_move']
                }
            ];

            workflowService.setActions(actions);
        }));

        it('can perform actions', inject(function(workflowService, $rootScope) {
            expect(workflowService.isActionAllowed({state: 'fetched'}, 'spike')).toBe(true);
            expect(workflowService.isActionAllowed({state: 'spiked'}, 'spike')).toBe(false);
            expect(workflowService.isActionAllowed({state: 'ingested'}, 'fetch_as_from_ingest')).toBe(true);
            expect(workflowService.isActionAllowed({state: 'draft'}, 'fetch_as_from_ingest')).toBe(false);
        }));
    });
});
