const phantom = require('phantom')
const sqlite = require('sqlite')

async function create_snapshot(username) {
  const instance = await phantom.create();
  const page = await instance.createPage();
  await page.on('onResourceRequested', function(requestData) {
    console.info('Requesting', requestData.url);
  });
 
  const status = await page.open(`https://instagram.com/${username}/`);

  page.render(`screenshots/${username}.jpg`)

  await instance.exit();
}

(async function() {
  const db = await sqlite.open('../db.sqlite3');
  const data = await db.all('SELECT username, filtered FROM followers')

  data.forEach( el => {
    console.log(el)
  })
}())
