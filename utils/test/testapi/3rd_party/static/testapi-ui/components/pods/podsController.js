/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

(function () {
    'use strict';

    angular
        .module('testapiApp')
        .controller('PodsController', PodsController);

    PodsController.$inject = [
        '$scope', '$http', '$filter', '$state', 'testapiApiUrl','raiseAlert'
    ];

    /**
     * TestAPI Pods Controller
     * This controller is for the '/pods' page where a user can browse
     * through pods declared in TestAPI.
     */
    function PodsController($scope, $http, $filter, $state, testapiApiUrl,
        raiseAlert) {
        var ctrl = this;

        ctrl.url = testapiApiUrl + '/pods';

        ctrl.create = create;
        ctrl.update = update;
        ctrl.open = open;
        ctrl.clearFilters = clearFilters;

        // ctrl.name = '';
        ctrl.new_name = '';
        ctrl.new_role = '';
        ctrl.new_mode = '';
        ctrl.new_details = '';

        ctrl.pageHeader = 'Pods';
        ctrl.pageParagraph = 'All declared ci or community pods are listed here.';

        /**
         * This is called when the date filter calendar is opened. It
         * does some event handling, and sets a scope variable so the UI
         * knows which calendar was opened.
         * @param {Object} $event - The Event object
         * @param {String} openVar - Tells which calendar was opened
         */
        function open($event, openVar) {
            $event.preventDefault();
            $event.stopPropagation();
            ctrl[openVar] = true;
        }

        /**
         * This function will clear all filters and update the results
         * listing.
         */
        function clearFilters() {
            ctrl.update();
        }

        /**
         * This will contact the TestAPI to create a new pod.
         */
        function create() {
            ctrl.showError = false;
            var pods_url = ctrl.url;
            var body = {
                name: ctrl.new_name,
                mode: ctrl.new_mode,
                role: ctrl.new_role,
                details: ctrl.new_details
            };

            ctrl.podsRequest =
                $http.post(pods_url, body).error(function (error) {
                    ctrl.showError = true;
                    ctrl.error =
                        'Error creating the new pod from server: ' +
                        angular.toJson(error);
                });
        }

        /**
         * This will contact the TestAPI to get a listing of declared pods.
         */
        function update() {
            ctrl.showError = false;
            ctrl.podsRequest =
                $http.get(ctrl.url).success(function (data) {
                    ctrl.data = data;
                }).error(function (error) {
                    ctrl.data = null;
                    ctrl.showError = true;
                    ctrl.error =
                        'Error retrieving pods from server: ' +
                        angular.toJson(error);
                });
        }

        function showPod(pod_name) {


        }
    }
})();
