: ${SERVER_URL:='http://testresults.opnfv.org/reporting/api'}

echo "var BASE_URL = 'http://${SERVER_URL}/landing-page'" >> app/scripts/app.config.js
echo "var PROJECT_URL = 'http://${SERVER_URL}'" >> app/scripts/app.config.js

apt-get install -y nodejs
apt-get install -y npm
npm install
npm install -g grunt
npm install -g bower
bower install --force --allow-root
grunt build
