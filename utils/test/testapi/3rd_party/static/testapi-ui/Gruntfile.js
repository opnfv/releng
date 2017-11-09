
module.exports = function (grunt) {
	require('load-grunt-tasks')(grunt);
	require('grunt-protractor-coverage')(grunt);
	grunt.loadNpmTasks('grunt-shell-spawn');
	grunt.loadNpmTasks('grunt-wait');
	grunt.loadNpmTasks('grunt-contrib-copy');
	grunt.loadNpmTasks('grunt-contrib-connect');
	grunt.initConfig({
		connect: {
			server: {
				options: {
					port: 8000,
					base: './',
					middleware: function(connect, options, middlewares) {
						middlewares.unshift(function(req, res, next) {
							if (req.method.toUpperCase() == 'POST') req.method='GET';
							return next();
						});
						return middlewares;
					}
				}
			}
		},
		copy: {
			assets: {
			  expand: true,
			  cwd: 'assets',
			  src: '**',
			  dest: 'testapi-ui/assets',
			},
			components: {
				expand: true,
				cwd: '../../../opnfv_testapi/ui',
				src: '**',
				dest: 'components',
			},
			copyComponents: {
				expand: true,
				cwd: 'components',
				src: '**',
				dest: 'testapi-ui/components',
			},
			shared: {
				expand: true,
				cwd: 'shared',
				src: '**',
				dest: 'testapi-ui/shared',
			},
			filesPng: {
				expand: true,
				src: '*.png',
				dest: 'testapi-ui/',
			},
			filesIco: {
				expand: true,
				src: '*.ico',
				dest: 'testapi-ui/',
			},
			filesJs: {
				expand: true,
				src: 'app.js',
				dest: 'testapi-ui/',
			},
			filesJson: {
				expand: true,
				src: 'config.json',
				dest: 'testapi-ui/',
			}
		},
		wait: {
			default: {
				options: {
					delay: 3000
				}
			}
		},
		shell: {
			updateSelenium: {
				command: 'node_modules/protractor/bin/webdriver-manager update',
				options: {
		      		async: false
		    	}
			},
			startSelenium: {
				command: 'node_modules/protractor/bin/webdriver-manager start',
				options: {
			      async: true
			    }
			},
			deleteFiles: {
				command: 'rm -r testapi-ui && rm -r components',
				options: {
			      async: false
			    }
			},
			options: {
		        stdout: false,
		        stderr: false
		    }
		},
		instrument: {
	        files: ['components/**/*.js'],
	        options: {
	        	lazy: false,
				basePath: "./testapi-ui/"
	        }
	    },
		karma: {
			unit: {
				configFile: '../../../opnfv_testapi/tests/UI/karma.conf.js'
			}
		},
		protractor_coverage: {
		    options: {
		        keepAlive: true,
		        noColor: false,
		        coverageDir: '../../../opnfv_testapi/tests/UI/coverage',
		        args: {
					specs: ['../../../opnfv_testapi/tests/UI/e2e/podsControllerSpec.js',
							'../../../opnfv_testapi/tests/UI/e2e/projectControllerSpec.js']
		        }
		    },
		    local: {
		        options: {
		            configFile: '../../../opnfv_testapi/tests/UI/protractor-conf.js'
		        }
		    }
		},
		makeReport: {
	        src: '../../../opnfv_testapi/tests/UI/coverage/*.json',
	        options: {
	            print: 'detail'
	        }
	    }
	});
	grunt.registerTask('test', [
		'karma:unit'
	]);
	grunt.registerTask('e2e', [
		'copy:assets',
		'copy:components',
		'copy:copyComponents',
		'copy:shared',
		'copy:filesPng',
		'copy:filesIco',
		'copy:filesJs',
		'copy:filesJson',
		'instrument',
		'connect',
		'shell:updateSelenium',
		'shell:startSelenium',
		'wait:default',
		'protractor_coverage',
		'makeReport',
		'shell:deleteFiles'

	]);
}
