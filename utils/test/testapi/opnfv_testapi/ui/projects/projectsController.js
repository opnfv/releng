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
        .controller('ProjectsController', ProjectsController);

        ProjectsController.$inject = [
        '$scope', '$http', '$filter', '$state', 'testapiApiUrl','raiseAlert'
    ];

    /**
     * TestAPI Project Controller
     * This controller is for the '/projects' page where a user can browse
     * through projects declared in TestAPI.
     */
    function ProjectsController($scope, $http, $filter, $state, testapiApiUrl,
        raiseAlert) {
        var ctrl = this;
        ctrl.url = testapiApiUrl + '/projects';
        ctrl.create = create;

        ctrl.createRequirements = [
            {label: 'name', type: 'text', required: true},
            {label: 'description', type: 'textarea', required: false}
        ];

        ctrl.name = '';
        ctrl.details = '';

        /**
         * This will contact the TestAPI to create a new project.
         */
        function create() {
            ctrl.showError = false;

            if(ctrl.name != ""){
                var projects_url = ctrl.url;
                var body = {
                    name: ctrl.name,
                    description: ctrl.description
                };
                if(~$scope.auth.projectNames.indexOf(ctrl.name)){
                    ctrl.projectsRequest =
                        $http.post(projects_url, body).error(function (data, status) {
                            ctrl.showError = true;
                            if(status == 403){
                                ctrl.error =
                                    'Error creating the new Project from server: Project\'s name already exists'
                            }else{
                                ctrl.error = 'Server is not responding';
                            }
                        });
                }else{
                    ctrl.showError = true;
                    ctrl.error = 'You do not have permission to perform this action.'
                }
                ctrl.name = "";
                ctrl.description="";
            }
            else{
                ctrl.showError = true;
                ctrl.error = 'Name is missing.'
            }
        }
    }
})();
