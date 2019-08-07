const phantom = require('phantom')
const sqlite = require('sqlite')
const fs = require('fs')

const create_snapshot = async users => {
  if (users.length == 0) {
    console.log("All done!")
    return
  }

  const u = users.shift()
  const filename = `target/${u.filtered ? `[${u.filtered}]` : ''}${u.username}.jpg`
  
  if (fs.existsSync(filename)) {
      return create_snapshot(users)
  }
  console.info(new Date().toLocaleTimeString(), u)
  const instance = await phantom.create()
  const page = await instance.createPage()

  const status = await page.open(`https://instagram.com/${u.username}/`)
  if (status !== 'success')
    console.warn(status, u.username)

  const pageHeight = await page.evaluate(function(text) {
    if (text) {
      var comment = document.createElement('div')
      comment.innerHTML = '<h1 style="color:red; padding-top:5px;">'+text+'</h1>'
      var header = document.querySelector("header section")
      header.appendChild(comment)
    }
    return document.body.scrollHeight;
  }, u.filtered)

  if (pageHeight > 900)
    page.property('clipRect', { width: 400, height: 900 })

  page.render(filename)

  await instance.exit();

  setTimeout(() => {
    create_snapshot(users)
  }, Math.min(Math.ceil(Math.random()*10), 5))
}

(async function() {
  const db = await sqlite.open('../db.sqlite3');
  const data = await db.all('SELECT username, filtered FROM followers ORDER BY RANDOM() LIMIT 500')
  
  await create_snapshot(data)
}())
