
module.exports = function (grunt) {
	require('load-grunt-tasks')(grunt);
	grunt.loadNpmTasks('grunt-shell-spawn');
	grunt.loadNpmTasks('grunt-wait');

	grunt.initConfig({
		wait: {
			default: {
				options: {
					delay: 1000
				}
			}
		},
		shell: {
			startServer: {
				command: 'opnfv-testapi',
			    options: {
			      async: true
			    }
			},
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
			options: {
		        stdout: false,
		        stderr: false
		    }
   		},
		karma: {
			unit: {
				configFile: 'karma.conf.js'
			}
		},
		protractor: {
			e2e: {
				options: {
					args: {
						specs: ['test/e2e/podsControllerSpec.js']
					},
					configFile: 'protractor.conf.js',
					keepAlive: true
				}
			}
		}
	});
	grunt.registerTask('test', [
		'karma:unit'
	]);
	grunt.registerTask('e2e', [
		'shell:updateSelenium',
		'shell:startServer',
		'shell:startSelenium',
		'wait:default',
		'protractor:e2e'
	]);
}
