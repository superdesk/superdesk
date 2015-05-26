define([
    './workflowService'
], function(workflowServiceSpec) {
    'use strict';

    describe('Workflow Service', function() {

        beforeEach(module(workflowServiceSpec.name));

        beforeEach(inject(function(preferencesService, $q, workflow) {
            var actions = [
                {
                    name: 'spike',
                    exclude_states: ['spiked', 'published', 'killed'],
                    privileges: ['spike']
                },
                {
                    name: 'fetch_from_ingest',
                    include_states: ['ingested'],
                    privileges: ['fetch']
                }
            ];

            workflow.setActions(actions);
        }));

        it('can perform actions', inject(function(workflow) {
            expect(workflow.isActionAllowed({state: 'fetched'}, 'spike')).toBe(true);
            expect(workflow.isActionAllowed({state: 'spiked'}, 'spike')).toBe(false);
            expect(workflow.isActionAllowed({state: 'ingested'}, 'fetch_from_ingest')).toBe(true);
            expect(workflow.isActionAllowed({state: 'draft'}, 'fetch_from_ingest')).toBe(false);
        }));
    });
});
