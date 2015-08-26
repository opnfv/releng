Creating/Configuring/Verifying Jenkins Jobs
============================================

Clone the repo::

 git clone ssh://YOU@gerrit.opnfv.org:29418/releng

make changes::

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

Follow the link to gerrit https://gerrit.opnfv.org/gerrit/51 in a few moments the verify job will have completed and you will see Verified +1 jenkins-ci in the gerrit ui.

If the changes pass the verify job https://build.opnfv.org/ci/view/builder/job/builder-verify-jjb/ The patch can be submitited by a committer.

Job Types

* Verify Job

 * Trigger: **recheck** or **reverify**

* Merge Job

 * Trigger: **remerge**

The verify and merge jobs are retriggerable in Gerrit by simply leaving a comment with one of the keywords listed above. This is useful in case you need to re-run one of those jobs in case if build issues or something changed with the environment.

You can add below persons as reviewers to your patch in order to get it reviewed and submitted.

* fatih.degirmenci@ericsson.com
* agardner@linuxfoundation.org
* trozet@redhat.com
* morgan.richomme@orange.com
* vlaza@cloudbasesolutions.com
* matthew.lijun@huawei.com
* pbandzi@cisco.com
* jose.lausuch@ericsson.com
* koffirodrigue@gmail.com
* r-mibu@cq.jp.nec.com

Or just email a request for submission to opnfv-helpdesk@rt.linuxfoundation.org

The Current merge and verify jobs for jenkins job builder as pulled from the repo::


**releng-jobs.yaml**:

.. code-block:: bash

 - project:
     name: builder-jobs
     jobs:
         - 'builder-verify-jjb'
         - 'builder-merge'
 
     project: 'releng'
 
 - job-template:
     name: builder-verify-jjb
 
     node: master
 
     project-type: freestyle
 
     logrotate:
         daysToKeep: 30
         numToKeep: 10
         artifactDaysToKeep: -1
         artifactNumToKeep: -1
 
     parameters:
         - project-parameter:
             project: '{project}'
         - gerrit-parameter:
             branch: 'master'
     scm:
         - gerrit-trigger-scm:
             credentials-id: '{ssh-credentials}'
             refspec: '$GERRIT_REFSPEC'
             choosing-strategy: 'gerrit'
 
     wrappers:
         - ssh-agent-credentials:
             user: '{ssh-credentials}'
 
     triggers:
         - gerrit:
             trigger-on:
                 - patchset-created-event:
                     exclude-drafts: 'false'
                     exclude-trivial-rebase: 'false'
                     exclude-no-code-change: 'false'
                 - draft-published-event
                 - comment-added-contains-event:
                     comment-contains-value: 'recheck'
                 - comment-added-contains-event:
                     comment-contains-value: 'reverify'
             projects:
               - project-compare-type: 'ANT'
                 project-pattern: 'releng'
                 branches:
                   - branch-compare-type: 'ANT'
                     branch-pattern: '**/master'
                 file-paths:
                     - compare-type: ANT
                       pattern: jjb/**
                     - compare-type: ANT
                       pattern: jjb-templates/**
 
 
     builders:
         - shell:
             !include-raw verify-releng
 
 - job-template:
     name: 'builder-merge'
 
     node: master
 
     # builder-merge job to run JJB update
     #
     # This job's purpose is to update all the JJB
 
     project-type: freestyle
 
     logrotate:
         daysToKeep: 30
         numToKeep: 40
         artifactDaysToKeep: -1
         artifactNumToKeep: 5
 
     parameters:
         - project-parameter:
             project: '{project}'
         - gerrit-parameter:
             branch: 'master'
 
     scm:
         - gerrit-trigger-scm:
             credentials-id: '{ssh-credentials}'
             refspec: ''
             choosing-strategy: 'default'
 
     wrappers:
         - ssh-agent-credentials:
             user: '{ssh-credentials}'
 
     triggers:
         - gerrit:
             trigger-on:
                 - change-merged-event
                 - comment-added-contains-event:
                     comment-contains-value: 'remerge'
             projects:
               - project-compare-type: 'ANT'
                 project-pattern: 'releng'
                 branches:
                     - branch-compare-type: 'ANT'
                       branch-pattern: '**/master'
                 file-paths:
                     - compare-type: ANT
                       pattern: jjb/**
 
     builders:
         - shell: |
                 source /opt/virtualenv/jenkins-job-builder/bin/activate
                 cd /opt/jenkins-ci/releng
                 git pull
                 jenkins-jobs update --delete-old jjb/
 
 


Revision: _sha1_

Build date:  _date_
