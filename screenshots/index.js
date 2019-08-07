const phantom = require('phantom')
const sqlite = require('sqlite')
const fs = require('fs')

async function create_snapshot(username) {
  const instance = await phantom.create();
  const page = await instance.createPage();
  // await page.on('onResourceRequested', function(requestData) {
  //   console.info('Requesting', requestData.url);
  // });
 
  const status = await page.open(`https://instagram.com/${username}/`);

  page.render(`target/${username}.jpg`)

  await instance.exit();
}

(async function() {
  const db = await sqlite.open('../db.sqlite3');
  const data = await db.all('SELECT username, filtered FROM followers LIMIT 100')
  let nextTimeout = 0
  data.forEach(el => {
    if (fs.existsSync(`target/${el.username}.jpg`))
      return

    nextTimeout = nextTimeout + Math.min(Math.ceil(Math.random()*10), 5)
    setTimeout(() => {
      create_snapshot(el.username)
    }, nextTimeout)
  })
}())
