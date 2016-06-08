# opnfv-testapi update

## How to use:

# backup mongodb,
# arguments:
# -u/--url: Mongo DB URL, default = mongodb://127.0.0.1:27017/
# -o/--output_dir: Output directory for the backup, default = ./
# the backup output will be put under dir/db__XXXX_XX_XX_XXXXXX/db
# -d/--db: database for the backup, default = test_results_collection
```
python backup.py
```

# restore mongodb
# arguments:
# -u/--url: Mongo DB URL, default = mongodb://127.0.0.1:27017/
# -i/--input_dir: Input directory for the Restore, must be specified
# the restore input must be specified to dir/db__XXXX_XX_XX_XXXXXX/db
# -d/--db: database name after the restore, default = basename of input_dir
```
python restore.py
```

# update mongodb
# arguments:
# -u/--url: Mongo DB URL, default = mongodb://127.0.0.1:27017/
# -d/--db: database name to be updated, default = test_results_collection
# changes need to be done:
# change collection name, modify changes.collections_old2New
# collections_old2New = {
#     'old_collection': 'new_collection',
# }
# change field name, modify changes.fields_old2New
# fields_old2New = {
#     'collection': [(query, {'old_field': 'new_field'})]
# }
# change the doc, modify changes.docs_old2New
# docs_old2New = {
#     'test_results': [
#         ({'field': 'old_value'}, {'field': 'new_value'}),
#         (query, {'field': 'new_value'}),
#     ]
# }
```
python update.py
```

# update opnfv-testapi process
# this script must be run right in this directory
# and remember to change ../etc/config.ini before running this script
# operations includes:
# kill running test_collection_api & opnfv-testapi
# install or update dependencies according to ../requirements.txt
# install opnfv-testapi
# run opnfv-testapi
```
python update_api.py
```
