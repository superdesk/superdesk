'use strict';

var lrSnippet = require('grunt-contrib-livereload/lib/utils').livereloadSnippet;

var mountFolder = function (connect, dir) {
  return connect.static(require('path').resolve(dir));
};

module.exports = function (grunt) {
  // load all grunt tasks
  require('matchdep').filterDev('grunt-*').forEach(grunt.loadNpmTasks);
  grunt.loadTasks('lib/grunt');

  // configurable paths
  var yeomanConfig = {
    app: 'app',
    dist: 'dist'
  };

  var serverConfig = {
    url: grunt.option('server') || 'http://localhost:5000'
  };

  try {
    yeomanConfig.app = require('./bower.json').appPath || yeomanConfig.app;
  } catch (e) {}

  grunt.initConfig({
    pkg: grunt.file.readJSON('./package.json'),
    
    yeoman: yeomanConfig,
    
    less: {
      development: {
        options: {
          paths: ["app/styles/less"],
          yuicompress: true
        },
        files: {
          "app/styles/css/bootstrap.css": "app/styles/less/bootstrap.less"
        }
      }
    },

    watch: {
      livereload: {
        options: {
          livereload: true
        },
        files: [
          '<%= yeoman.app %>/{,*/}*.html',
          '{.tmp,<%= yeoman.app %>}/styles/css/custom.css',
          '{.tmp,<%= yeoman.app %>}/styles/{,*/}*.less',
          '{.tmp,<%= yeoman.app %>}/{,*/}*.js',
          '<%= yeoman.app %>/images/{,*/}*.{png,jpg,jpeg,gif,webp,svg}'
        ],
        tasks: ['less']
      }
    },
    connect: {
      options: {
        port: 9000,
        // Change this to '0.0.0.0' to access the server from outside.
        hostname: 'localhost'
      },
      livereload: {
        options: {
          middleware: function (connect) {
            return [
              lrSnippet,
              mountFolder(connect, '.tmp'),
              mountFolder(connect, yeomanConfig.app),
              mountFolder(connect, 'dist')
            ];
          }
        }
      },
      test: {
        options: {
          middleware: function (connect) {
            return [
              mountFolder(connect, '.tmp'),
              mountFolder(connect, 'test')
            ];
          }
        }
      }
    },
    open: {
      server: {
        url: 'http://localhost:<%= connect.options.port %>'
      }
    },
    clean: {
      dist: {
        files: [{
          dot: true,
          src: [
            '.tmp',
            '<%= yeoman.dist %>/*',
            '!<%= yeoman.dist %>/.git*'
          ]
        }]
      },
      server: '.tmp'
    },
    jshint: {
      options: {
        jshintrc: '.jshintrc',

      },
      all: [
        //'Gruntfile.js',
        '<%= yeoman.app %>/main.js',
        '<%= yeoman.app %>/superdesk/{,*/}*.js'
      ]
    },
    karma: {
      unit: {
        configFile: 'karma.conf.js',
        singleRun: true,
        autoWatch: false
      }
    },
    copy: {
      dist: {
        files: [{
          expand: true,
          dot: true,
          cwd: '<%= yeoman.app %>',
          dest: '<%= yeoman.dist %>',
          src: [
            '*.{ico,txt,html}',
            '.htaccess',
            'images/**/*',
            'styles/{,*/}*.css',
            'scripts/**/*',
            'config.js'
          ]
        }]
      }
    },
    write: {
      config: {
        file: '<%= yeoman.dist %>/config.js',
        content: 'ServerConfig = ' + JSON.stringify(serverConfig) + ";\n",
      }
    },
    compress: {
      build: {
        options: {archive: 'dist/<%= pkg.name %>.zip', mode: 'zip'},
        src: ['**'], cwd: '<%= yeoman.dist %>', expand: true, dot: true, dest: '<%= pkg.name %>/'
      }
    }
    
    

  });

  grunt.registerTask('server', [
    'clean:server',
    'write:config',
    'less',
    'connect:livereload',
    'open',
    'watch'
  ]);

  grunt.registerTask('test', [
    'clean:server',
    'connect:test',
    'karma'
  ]);

  grunt.registerTask('build', [
    'clean:dist',
    'write:config',
    'jshint',
    'less',
    'test',
    'copy'
  ]);

  grunt.registerTask('default', ['build']);
  grunt.registerTask('package', ['build', 'compress']);
};
