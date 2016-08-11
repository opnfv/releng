===========================================
Creating/Configuring/Verifying Jenkins Jobs
===========================================

<li><a href="//pdfcrowd.com/url_to_pdf/">Save to PDF - normal</a></li>
<li><a href="//pdfcrowd.com/url_to_pdf/?pdf_scaling_factor=0.7">Save to PDF - pdf_scaling_factor=0.7</a></li>
<li><a href="//pdfcrowd.com/url_to_pdf/?pdfcrowd_logo=false">Save to PDF - pdfcrowd_logo=false</a></li>
<li><a href="//pdfcrowd.com/url_to_pdf/?footer_html=build:%202016-08">Save to PDF - footer_html=build:%202016-08</a></li>
<li><a href="//pdfcrowd.com/url_to_pdf/?pdf_scaling_factor=0.7&pdfcrowd_logo=false&footer_html=build:%202016-08">Save to PDF - all</a></li>

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

The verify and merge jobs are retriggerable in Gerrit by simply leaving
a comment with one of the keywords listed above.
This is useful in case you need to re-run one of those jobs in case
if build issues or something changed with the environment.

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

Or Add the group releng-contributors

Or just email a request for submission to opnfv-helpdesk@rt.linuxfoundation.org

The Current merge and verify jobs for jenkins job builder can be found
in `releng-jobs.yaml`_.

.. _releng-jobs.yaml:
    https://gerrit.opnfv.org/gerrit/gitweb?p=releng.git;a=blob;f=jjb/releng-jobs.yaml;
