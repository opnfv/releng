import hudson.model.*
if (manager.build.@result == hudson.model.Result.FAILURE) {
    manager.build.@result = hudson.model.Result.UNSTABLE
}
