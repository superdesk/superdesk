module.exports = {
    build: {
        options: {archive: '<%= distDir %>/<%= pkg.name %>.zip', mode: 'zip'},
        src: ['**'], cwd: '<%= distDir %>', expand: true, dot: true, dest: '<%= pkg.name %>/'
    }
};
