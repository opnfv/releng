import hudson.model.*
if (manager.logContains("^.*apex-deploy-baremetal.*SUCCESS$")
      && manager.build.@result == hudson.model.Result.FAILURE) {
    manager.build.@result = hudson.model.Result.UNSTABLE
}
