const path = require('path');
const execSync = require('child_process').execSync;
const dir = path.join(require.resolve('superdesk-core/package.json'), '../tasks/build-extensions');

function cleanUp() {
    execSync('rm -r build-extensions', {stdio: 'inherit'});
    process.exit();
}

process.on('exit', cleanUp);

process.on('SIGINT', () => {
    process.exit();
});

const forwardOptions = process.argv.slice(2).join(' ')

execSync(`cp -r ${dir} ./`, {stdio: 'inherit'});
execSync(`node build-extensions/index.js ${forwardOptions}`, {stdio: 'inherit'});

