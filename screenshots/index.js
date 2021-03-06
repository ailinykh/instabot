const phantom = require('phantom')
const sqlite = require('sqlite')
const fs = require('fs')

const create_snapshots = async users => {
  if (users.length == 0) {
    console.log("🎉  All done!")
    console.info('await before exiting')
    await instance.exit()
    return
  }

  const u = users.shift()
  const filename = `target/${u.filtered ? `[${u.filtered}]` : ''}${u.username}.jpg`
  
  if (fs.existsSync(filename)) {
      return create_snapshots(users)
  }

  await create_snapshot(u, filename)

  setTimeout(() => {
    create_snapshots(users)
  }, Math.floor(Math.random() * 5) + 1) // Timeout 1..5 sec
}

const create_snapshot = async (u, filename) => {
  
  console.info(new Date().toLocaleTimeString(), u)
  
  const status = await page.open(`https://www.instagram.com/${u.username}/`)
  if (status !== 'success') {
    console.warn(status, u.username)
    // recreate on fail https://stackoverflow.com/questions/32430426/
    instance = await phantom.create()
    page = await instance.createPage()
    await new Promise(success => { setTimeout(()=>{ success() }, 5000) }) // timeout
    return
  }

  await new Promise(success => {
    setTimeout(()=>{ success() }, 1000) // await media load
  })

  const pageHeight = await page.evaluate(function(text) {
    if (text) {
      var comment = document.createElement('div')
      comment.innerHTML = '<h1 style="color:red; padding-top:5px;">'+text+'</h1>'
      var header = document.querySelector("header section")
      header.appendChild(comment)
    }
    return document.body.scrollHeight;
  }, u.filtered)

  page.property('clipRect', { width: 400, height: Math.min(pageHeight, 900) })

  page.render(filename)
}

var instance
var page 

(async function() {
  const db = await sqlite.open('../db.sqlite3');
  const data = await db.all('SELECT username, filtered FROM followers ORDER BY RANDOM() LIMIT 5000')
  await db.close()

  instance = await phantom.create()
  page = await instance.createPage()
  await create_snapshots(data)
}())
