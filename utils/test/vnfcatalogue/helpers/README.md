# Helper Directory

## Helper to migrate database

First make sure nodejs and mysql are installed. Then use

```bash
npm install bookshelf mysql knex when lodash --save
```

Create a database named **vnf_catalogue**.
Enter the mysql credentials in migrate.js.

Then use

```bash
node migrate
```

If successful the script will return success message. The current script is
idempotent is nature, if run twice it will just return error and write nothing.

