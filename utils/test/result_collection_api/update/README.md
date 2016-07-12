Welcome to TESTAPI Update!
========================


This file is used to describe how testapi update works

----------
How to use
---------------

#### <i class="icon-file"></i> backup mongodb

arguments:
: -u/--url: Mongo DB URL, default = mongodb://127.0.0.1:27017/
the backup output will be put under dir/db__XXXX_XX_XX_XXXXXX/db
-d/--db: database for the backup, default = test_results_collection

usage:
```
python backup_mongodb.py
```

#### <i class="icon-file"></i> restore mongodb

arguments:
: -u/--url: Mongo DB URL, default = mongodb://127.0.0.1:27017/
  -i/--input_dir: Input directory for the Restore, must be specified,
  the restore input must be specified to dir/db__XXXX_XX_XX_XXXXXX/db
  -d/--db: database name after the restore, default = basename of input_dir

usage:
```
python restore_mongodb.py
```
#### <i class="icon-file"></i> update mongodb

 arguments:
: -u/--url: Mongo DB URL, default = mongodb://127.0.0.1:27017/
 -d/--db: database name to be updated, default = test_results_collection

changes need to be done:
change collection name, modify changes.collections_old2New
 > collections_old2New = {
     'old_collection': 'new_collection',
 }

 change field name, modify changes.fields_old2New
 > fields_old2New = {
     'collection': [(query, {'old_field': 'new_field'})]
 }

 change the doc, modify changes.docs_old2New
 > docs_old2New = {
     'test_results': [
         ({'field': 'old_value'}, {'field': 'new_value'}),
         (query, {'field': 'new_value'}),
     ]
 }

#### <i class="icon-file"></i> update opnfv-testapi process
This script must be run right in this directory and remember to
change ../etc/config.ini before running this script.

operations includes:
: kill running test_collection_api & opnfv-testapi
install or update dependencies according to ../requirements.txt
install opnfv-testapi
run opnfv-testapi

usage:
```
python update_api.py
```
#### <i class="icon-file"></i> update opnfv/testapi container
Here ansible-playbook is used to implement auto update.
Please make sure that the remote server is accessible via ssh.

install ansible, please refer:
```
http://docs.ansible.com/ansible/intro_installation.html
```
run update.yml
arguments:
: host: remote server, must provide
user: user used to access to remote server, default to root
port: exposed port used to access to testapi, default to 8000
image: testapi's docker image, default to opnfv/testapi:latest
update_path: templates directory in remote server, default to /tmp/testapi
mongodb_url: url of mongodb, default to 172.17.0.1, docker0 ip
swagger_url: swagger access url, default to http://host:port

usage:
```
ansible-playbook update.yml --extra-vars "
host=10.63.243.17
user=zte
port=8000
image=opnfv/testapi
update_path=/tmp/testapi
mongodb_url=mongodb://172.17.0.1:27017
swagger_url=http://10.63.243.17:8000"```
> **Note:**

> - If documents need to be changed, please modify file
templates/changes_in_mongodb.py, and refer section **update mongodb**
