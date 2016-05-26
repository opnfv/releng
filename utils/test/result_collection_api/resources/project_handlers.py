from tornado import gen
from tornado.web import HTTPError, asynchronous

from tornado_swagger_ui.tornado_swagger import swagger
from handlers import GenericApiHandler, prepare_put_request, format_data
from common.constants import HTTP_BAD_REQUEST, HTTP_FORBIDDEN, HTTP_NOT_FOUND
from project_models import Project


class GenericProjectHandler(GenericApiHandler):
    def __init__(self, application, request, **kwargs):
        super(GenericProjectHandler, self).__init__(application,
                                                    request,
                                                    **kwargs)
        self.table = 'projects'
        self.table_cls = Project


class ProjectCLHandler(GenericProjectHandler):
    @swagger.operation(nickname="list-all")
    def get(self):
        """
            @description: list all projects
            @return 200: return all projects, empty list is no project exist
            @rtype: L{Projects}
        """
        self._list()

    @swagger.operation(nickname="create")
    def post(self):
        """
            @description: create a project
            @param body: project to be created
            @type body: L{ProjectCreateRequest}
            @in body: body
            @rtype: L{Project}
            @return 200: project is created.
            @raise 403: project already exists
            @raise 400: post without body
        """
        self._create('{} already exists as a {}')


class ProjectGURHandler(GenericProjectHandler):
    @swagger.operation(nickname='get-one')
    def get(self, project_name):
        """
            @description: get a single project by project_name
            @rtype: L{Project}
            @return 200: project exist
            @raise 404: project not exist
        """
        self._get_one({'name': project_name})

    @asynchronous
    @gen.coroutine
    @swagger.operation(nickname="update")
    def put(self, project_name):
        """
            @description: update a single project by project_name
            @param body: project to be updated
            @type body: L{ProjectUpdateRequest}
            @in body: body
            @rtype: L{Project}
            @return 200: update success
            @raise 404: project not exist
            @raise 403: new project name already exist or nothing to update
        """
        if self.json_args is None:
            raise HTTPError(HTTP_BAD_REQUEST)

        query = {'name': project_name}
        from_project = yield self.db.projects.find_one(query)
        if from_project is None:
            raise HTTPError(HTTP_NOT_FOUND,
                            "{} could not be found".format(project_name))

        project = Project.from_dict(from_project)
        new_name = self.json_args.get("name")
        new_description = self.json_args.get("description")

        # check for payload name parameter in db
        # avoid a request if the project name has not changed in the payload
        if new_name != project.name:
            to_project = yield self.db.projects.find_one(
                {"name": new_name})
            if to_project is not None:
                raise HTTPError(HTTP_FORBIDDEN,
                                "{} already exists as a project"
                                .format(new_name))

        # new dict for changes
        request = dict()
        request = prepare_put_request(request,
                                      "name",
                                      new_name,
                                      project.name)
        request = prepare_put_request(request,
                                      "description",
                                      new_description,
                                      project.description)

        """ raise exception if there isn't a change """
        if not request:
            raise HTTPError(HTTP_FORBIDDEN, "Nothing to update")

        """ we merge the whole document """
        edit_request = project.format()
        edit_request.update(request)

        """ Updating the DB """
        yield self.db.projects.update(query, edit_request)
        new_project = yield self.db.projects.find_one({"_id": project._id})

        self.finish_request(format_data(new_project, Project))

    @swagger.operation(nickname='delete')
    def delete(self, project_name):
        """
            @description: delete a project by project_name
            @return 200: delete success
            @raise 404: project not exist
        """
        self._delete({'name': project_name})
