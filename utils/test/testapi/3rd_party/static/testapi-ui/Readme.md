1. Install Grunt Globally
	`npm install -g  grunt-cli` 

2. Install Protractor Globally
	
	`npm install protractor`

3. Update the web driver
	
	`./node_modules/protractor/bin/webdriver-manager update`

4. Inside the prject folder run npm install
	
	`npm install`

5. For unit test 
	
	`grunt test`

6. For e2e test 
	
	* Start web driver

		`./node_modules/protractor/bin/webdriver-manager start`
	* Then 
		
		`grunt e2e`