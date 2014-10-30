module.exports = {
    build: {
        options: {archive: '<%= serverDir %>/<%= pkg.name %>.zip', mode: 'zip'},
        src: ['**'], cwd: '<%= serverDir %>', expand: true, dot: true, dest: '<%= pkg.name %>/'
    }
};
