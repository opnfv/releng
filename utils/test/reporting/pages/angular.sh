: ${SERVER_URL:='http://testresults.opnfv.org/reporting/api'}

echo "var BASE_URL = 'http://${SERVER_URL}/landing-page'" > app/scripts/app.config.js

apt-get install -y nodejs
apt-get install -y npm
npm install
npm install -g grunt bower
bower install --allow-root
grunt build
