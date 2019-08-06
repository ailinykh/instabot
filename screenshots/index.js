const phantom = require('phantom');
const sqlite3 = require('sqlite3').verbose();

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

const get_users = async () => {
  let db = new sqlite3.Database('../db.sqlite3', sqlite3.OPEN_READONLY, err => {
    if (err)
        return console.error(err.message)
    console.log('Connected to database.')
  })
  
  await db.serialize()
  console.log('Database serialized')

  let rows = await db.each(`SELECT username, filtered FROM followers`)
  console.log('Got rows')
  // db.serialize(async () => {
  //     await db.each(`SELECT username, filtered FROM followers`, async (err, row) => {
  //         if (err) {
  //             console.error(err.message);
  //         }
  //         console.log(row.username + "\t" + row.filtered);
  //         users.push(row)
  //         // await create_snapshot(row.username)
  //     })
  // })
  
  db.close()

  return rows
}

const main = async () => {
  const users = await get_users()

  console.log(`I'm done! ${users.length}`)
}

(async function() {
  await main()
}())

// setTimeout(() => {}, 10000)

// for(var i=0; i<100; i++)
  // console.log(Math.min(Math.ceil(Math.random()*10), 5))


/*
(async function() {
  const instance = await phantom.create();
  const page = await instance.createPage();
  await page.on('onResourceRequested', function(requestData) {
    console.info('Requesting', requestData.url);
  });
 
  const status = await page.open('https://instagram.com/anikoyoga/');
//   const content = await page.property('content');
//   console.log(content);
 
  page.render('image.jpg')

  await instance.exit();
})();
*/