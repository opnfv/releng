'use strict';

var mock = require('protractor-http-mock');
var baseURL = "http://localhost:8000"

describe('testing the Project Link for anonymous user', function () {

	it( 'should not show the Project Link for anonymous user', function() {
        mock.teardown();
		browser.get(baseURL);
        var projectslink = element(by.linkText('Projects'));
        expect(projectslink.isPresent()).toBe(true);
    });

    it( 'navigate anonymous user to project page', function() {
        browser.get(baseURL+'#/projects');
        var EC = browser.ExpectedConditions;
        browser.wait(EC.urlContains(baseURL+ '/#/projects'), 10000);
    });

    it('create button is not visible for anonymous user ', function () {
        browser.get(baseURL+'#/projects');
        var buttonCreate = element(by.buttonText('Create'));
        expect(buttonCreate.isDisplayed()).toBeFalsy();
    });

});

describe('testing the Project Link for user who is not in submitter group', function () {
        beforeEach(function(){
            mock([
                {
                    request: {
                    path: '/api/v1/profile',
                    method: 'GET'
                    },
                    response: {
                        data: {
                            "fullname": "Test User", "_id": "79f82eey9a00c84bfhc7aed",
                            "user": "testUser", "groups": ["opnfv-testapi-users"],
                            "email": "testuser@test.com"
                        }
                    }
                }
            ]);
        });

        it( 'should show the Project Link for user', function() {
            browser.get(baseURL);
            var projectslink = element(by.linkText('Projects'));
            expect(projectslink.isPresent()).toBe(true);
        });

        it( 'should navigate the user to the Project page', function() {
            browser.get(baseURL);
            var projectslink = element(by.linkText('Projects')).click();
            var EC = browser.ExpectedConditions;
            browser.wait(EC.urlContains(baseURL+ '/#/projects'), 10000);
        });

        it('create button is not visible for user', function () {
            browser.get(baseURL+'#/projects');
            var buttonCreate = element(by.buttonText('Create'));
            expect(buttonCreate.isDisplayed()).toBeFalsy();
        });
})

describe('testing the Project Link for user who is in submitter group', function () {
    beforeEach(function(){
        mock([
            {
                request: {
                    path: '/api/v1/profile',
                    method: 'GET'
                },
                response: {
                    data: {
                        "fullname": "Test User", "_id": "79f82eey9a00c84bfhc7aed",
                        "user": "testUser", "groups": ["opnfv-testapi-users",
                        "opnfv-gerrit-testProject1-submitters",
                        "opnfv-gerrit-testProject2-submitters" ],
                        "email": "testuser@test.com"
                    }
                }
            },
            {
							request: {
								path: '/api/v1/projects',
								method: 'POST'
							},
							response: {
								data: {
									href: baseURL+"/api/v1/projects/testProject1"
								}
							}
            },
            {
							request: {
								path: '/api/v1/projects',
								method: 'POST',
								data: {
									name: 'testProject2',
									description : 'demoDescription',
								}
							},
							response: {
								status : 403
							}
						},
            {
							request: {
								path: '/api/v1/projects',
								method: 'POST',
								data: {
									name: 'testProject3',
									description : 'demoDescription',
								}
							},
							response: {
								status : 403,
								data : 'You do not have permission to perform this action'
							}
						}
        ]);
    });

    it( 'should show the Project Link for user', function() {
        browser.get(baseURL);
        var projectslink = element(by.linkText('Projects'));
        expect(projectslink.isPresent()).toBe(true);
    });

    it( 'should navigate the user to the Project page', function() {
        browser.get(baseURL);
        var projectslink = element(by.linkText('Projects')).click();
        var EC = browser.ExpectedConditions;
        browser.wait(EC.urlContains(baseURL+ '/#/projects'), 10000);
    });

    it('create button is visible for user', function () {
        browser.get(baseURL+'#/projects');
        var buttonCreate = element(by.buttonText('Create'));
        expect(buttonCreate.isDisplayed()).toBe(true);
    });

	it('Show error when user click the create button with a empty name', function () {
		browser.get(baseURL+ '/#/projects');
		var description = element(by.model('ctrl.description'));
		description.sendKeys('DemoDescription');
		var buttonCreate = element(by.buttonText('Create'));
		buttonCreate.click();
        expect(element(by.cssContainingText(".alert","Name is missing."))
        .isDisplayed()).toBe(true);
	});

	it('Show error when user click the create button with an already existing name', function () {
		browser.get(baseURL+ '/#/projects');
		var name = element(by.model('ctrl.name'));
		var details = element(by.model('ctrl.description'));
		name.sendKeys('testProject2');
		details.sendKeys('demoDescription');
		var buttonCreate = element(by.buttonText('Create'));
		buttonCreate.click();
        expect(element(by.cssContainingText(".alert",
        "Error creating the new Project from server:undefined"))
        .isDisplayed()).toBe(true);
    });

    it('Show error when user try to create a project which he is not belonged to ', function () {
		browser.get(baseURL+ '/#/projects');
		var name = element(by.model('ctrl.name'));
		var details = element(by.model('ctrl.description'));
		name.sendKeys('testProject3');
		details.sendKeys('demoDescription');
		var buttonCreate = element(by.buttonText('Create'));
        buttonCreate.click();
        expect(element(by.cssContainingText(".alert",
        'Error creating the new Project from server:"You do not have permission to perform this action"')).isDisplayed())
        .toBe(true);
    });

	it('Do not show error if input is acceptable', function () {
		var name = element(by.model('ctrl.name'));
		var details = element(by.model('ctrl.description'));
		name.sendKeys('testProject1');
		details.sendKeys('demoDescription');
		var buttonCreate = element(by.buttonText('Create'));
		buttonCreate.click().then(function(){
            expect(element(by.cssContainingText(".alert",
            "Create Success"))
            .isDisplayed()).toBe(true);
		});
    });

	it('If backend is not responding then show error when user click the create button',function(){
		mock.teardown();
		mock([
            {
                request: {
                    path: '/api/v1/profile',
                    method: 'GET'
                },
                response: {
                    data: {
                        "fullname": "Test User", "_id": "79f82eey9a00c84bfhc7aed",
                        "user": "testUser", "groups": ["opnfv-testapi-users",
                        "opnfv-gerrit-testProject1-submitters",
                        "opnfv-gerrit-testProject2-submitters" ],
                        "email": "testuser@test.com"
                    }
                }
            }
		]);
		browser.get(baseURL+ '/#/projects');
		var name = element(by.model('ctrl.name'));
		var details = element(by.model('ctrl.description'));
		name.sendKeys('testProject1');
		details.sendKeys('demoDescription');
		var buttonCreate = element(by.buttonText('Create'));
		buttonCreate.click().then(function(){
			expect(element(by.css(".alert.alert-danger.ng-binding.ng-scope")).isDisplayed()).toBe(true);
        });
	});
})
