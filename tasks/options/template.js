
module.exports = function(grunt) {
    var index = {'<%= distDir %>/index.html': '<%= appDir %>/index.html'},
        envs = {
            dev: 'http://localhost:5000',
            prod: 'http://superdesk-api.herokuapp.com',
            test: 'http://superdesk.apiary.io'
        };

    return require('lodash').mapValues(envs, function(defaultServer) {
        return {
            files: index,
            options: {
                data: {server: {url: grunt.option('server') || defaultServer}}
            }
        };
    });
};
