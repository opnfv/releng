'use strict';

var mock = require('protractor-http-mock');
var baseURL = "http://localhost:8000"
describe('testing the Pods page for anonymous user', function () {

	beforeEach(function(){
		mock([{
			request: {
			  path: '/api/v1/pods',
			  method: 'GET'
			},
			response: {
				data: {
					pods: [{role: "community-ci", name: "test", owner: "testUser", details: "DemoDetails", mode: "metal", _id: "59f02f099a07c84bfc5c7aed", creation_date: "2017-10-25 11:58:25.926168"}]
				}
			}
		  }]);
	});

	it( 'should navigate to pods link ', function() {
		browser.get(baseURL);
		var podslink = element(by.linkText('Pods')).click();
		var EC = browser.ExpectedConditions;
		browser.wait(EC.urlContains(baseURL+ '/#/pods'), 10000);
	});

	it('create button is not visible for anonymous user', function () {
		browser.get(baseURL+'#/pods');
		var buttonCreate = element(by.buttonText('Create'));
		expect(buttonCreate.isDisplayed()).toBeFalsy();
	});

	it('filter button is visible for anonymous user', function () {
		var buttonFilter = element(by.buttonText('Filter'));
		expect(buttonFilter.isDisplayed()).toBe(true)
	});

	it('clear button is visible for anonymous user', function () {
		var buttonClear = element(by.buttonText('Clear'));
		expect(buttonClear.isDisplayed()).toBe(true)
	});

	it('Show results when click filter button', function () {
		var buttonFilter = element(by.buttonText('Filter'));
		buttonFilter.click();
		var pod = element(by.css('.show-pod'));
		expect(pod.isPresent()).toBe(true);
	});

	it('Show results when click clear button', function () {
		browser.get(baseURL+'#/pods');
		var buttonClear = element(by.buttonText('Clear'));
		buttonClear.click();
		var pod = element(by.css('.show-pod'));
		expect(pod.isPresent()).toBe(true);
	});

	it('If details is not shown then show details when click the link',function() {
		expect(element(by.css('.show-pod.hidden')).isPresent()).toBe(true);
		var podslink = element(by.linkText('test')).click();
		expect(element(by.css('.show-pod.hidden')).isPresent()).toBe(false);
	});

	it('If details is shown then hide details when click the link',function() {
		expect(element(by.css('.show-pod.hidden')).isPresent()).toBe(false);
		var podslink = element(by.linkText('test')).click();
		expect(element(by.css('.show-pod.hidden')).isPresent()).toBe(true);
	});

	it('If backend is not responding then show error when click filter button', function () {
		browser.get(baseURL + '/#/pods');
		mock.teardown();
		var buttonFilter = element(by.buttonText('Filter'));
		buttonFilter.click().then(function(){
			expect(element(by.css('.alert.alert-danger.ng-binding.ng-scope')).isDisplayed()).toBe(true);
		});
	});

});

describe('testing the Pods page for authorized user', function () {

	beforeEach(function(){
		mock([
			{
				request: {
				  path: '/api/v1/pods',
				  method: 'POST'
				},
				response: {
					data: {
						href: baseURL+"/api/v1/pods/test"
					}
				}
			  },
			  {
				request: {
				  path: '/api/v1/pods',
				  method: 'POST',
				  data: {
					name: 'test1',
					details : 'DemoDetails',
					role : 'community-ci',
					mode : 'metal'
				  }
				},
				response: {
					status : 403
				}
			  },
			  {
				request: {
				path: '/api/v1/profile',
				method: 'GET'
				},
				response: {
					data: {
						"fullname": "Test User", "_id": "79f82eey9a00c84bfhc7aed", "user": "testUser", "groups": ["opnfv-testapi-users"], "email": "testuser@test.com"
					}
				}
			}
		]);
	});

	it('create button is visible for authorized user', function () {
		browser.get(baseURL + '/#/pods');
		var buttonCreate = element(by.buttonText('Create'));
		expect(buttonCreate.isDisplayed()).toBe(true);
	});

	it('Do not show error if input is acceptable', function () {
		var name = element(by.model('ctrl.name'));
		var details = element(by.model('ctrl.details'));
		name.sendKeys('test');
		details.sendKeys('DemoDetails');
		var buttonCreate = element(by.buttonText('Create'));
		buttonCreate.click().then(function(){
			expect(element(by.css('.alert.alert-danger.ng-binding.ng-scope')).isDisplayed()).toBe(false);
		});
	});

	it('Show error when user click the create button with a empty name', function () {
		browser.get(baseURL+ '/#/pods');
		var details = element(by.model('ctrl.details'));
		details.sendKeys('DemoDetails');
		var buttonCreate = element(by.buttonText('Create'));
		buttonCreate.click();
		expect(element(by.cssContainingText(".alert","Name is missing.")).isDisplayed()).toBe(true);
	});

	it('Show error when user click the create button with an already existing name', function () {
		browser.get(baseURL+ '/#/pods');
		var name = element(by.model('ctrl.name'));
		var details = element(by.model('ctrl.details'));
		name.sendKeys('test1');
		details.sendKeys('DemoDetails');
		var buttonCreate = element(by.buttonText('Create'));
		buttonCreate.click();
		expect(element(by.cssContainingText(".alert","Error creating the new pod from server: Pod's name already exists")).isDisplayed()).toBe(true);
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
						"fullname": "Test User", "_id": "79f82eey9a00c84bfhc7aed", "user": "testUser", "groups": ["opnfv-testapi-users"], "email": "testuser@test.com"
					}
				}
			}
		]);
		browser.get(baseURL+ '/#/pods');
		var name = element(by.model('ctrl.name'));
		var details = element(by.model('ctrl.details'));
		name.sendKeys('test');
		details.sendKeys('DemoDetails');
		var buttonCreate = element(by.buttonText('Create'));
		buttonCreate.click().then(function(){
			expect(element(by.css('.alert.alert-danger.ng-binding.ng-scope')).isDisplayed()).toBe(true);
		});
	})
});