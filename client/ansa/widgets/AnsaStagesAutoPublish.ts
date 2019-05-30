
export default function AnsaStagesAutoPublish (desks, api) {
    desks.initialize().then(() => {
        const desk = desks.getCurrentDesk();
        if (!desk) { // only works in desk context
            return;
        }

        this.stages = desks.deskStages[desk._id];
    });

    this.toggle = (stage) => {
        stage.auto_publish = !stage.auto_publish;
        this.save(stage);
    };

    this.save = (stage) => {
        api.save('stages', stage, {auto_publish: stage.auto_publish});
    };
};

AnsaStagesAutoPublish.$inject = ['desks', 'api'];
