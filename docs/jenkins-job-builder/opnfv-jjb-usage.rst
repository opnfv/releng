===========================================
Creating/Configuring/Verifying Jenkins Jobs
===========================================

Clone and setup the repo::

    git clone ssh://YOU@gerrit.opnfv.org:29418/releng
    cd releng
    git review -s

Make changes::

    git commit -sv
    git review
    remote: Resolving deltas: 100% (3/3)
    remote: Processing changes: new: 1, refs: 1, done
    remote:
    remote: New Changes:
    remote:   https://gerrit.opnfv.org/gerrit/51
    remote:
    To ssh://agardner@gerrit.opnfv.org:29418/releng.git
     * [new branch]      HEAD -> refs/publish/master

Test with tox::

    tox -v -ejjb

Submit the change to gerrit::

    git review -v

Follow the link to gerrit https://gerrit.opnfv.org/gerrit/51 in a few moments
the verify job will have completed and you will see Verified +1 jenkins-ci in
the gerrit ui.

If the changes pass the verify job
https://build.opnfv.org/ci/view/builder/job/builder-verify-jjb/ ,
the patch can be submitited by a committer.

Job Types

* Verify Job

  * Trigger: **recheck** or **reverify**

* Merge Job

  * Trigger: **remerge**

* Experimental Job

  * Trigger: **check-experimental**

The verify and merge jobs are retriggerable in Gerrit by simply leaving
a comment with one of the keywords listed above.
This is useful in case you need to re-run one of those jobs in case
if build issues or something changed with the environment.

The experimental jobs are not triggered automatically. You need to leave
a comment with the keyword list above to trigger it manually. It is useful
for trying out experimental features.

Note that, experimental jobs `skip vote`_ for verified status, which means
it will reset the verified status to 0. If you want to keep the verified
status, use **recheck-experimental** in commit message to trigger both
verify and experimental jobs.

You can add below persons as reviewers to your patch in order to get it
reviewed and submitted.

* fatih.degirmenci@ericsson.com
* agardner@linuxfoundation.org
* trozet@redhat.com
* morgan.richomme@orange.com
* vlaza@cloudbasesolutions.com
* matthew.lijun@huawei.com
* meimei@huawei.com
* jose.lausuch@ericsson.com
* koffirodrigue@gmail.com
* r-mibu@cq.jp.nec.com
* tbramwell@linuxfoundation.org

Or Add the group releng-contributors

Or just email a request for submission to opnfv-helpdesk@rt.linuxfoundation.org

The Current merge and verify jobs for jenkins job builder can be found
in `releng-jobs.yaml`_.

.. _releng-jobs.yaml:
    https://gerrit.opnfv.org/gerrit/gitweb?p=releng.git;a=blob;f=jjb/releng-jobs.yaml;
.. _skip vote:
    https://wiki.jenkins-ci.org/display/JENKINS/Gerrit+Trigger#GerritTrigger-SkipVote
