/*
 *  Find and remove files which have profile picture loaded with error
 */
const fs = require('fs')
const pixels = require('image-pixels')


const equall = (a1, a2) => {
    if (!a1 || !a2 || a1.length != a2.length)
        return false

    let res = true
    
    a1.forEach((e1, i) => {
        if (e1 !== a2[i])
            res = false
    })

    return res
}

const getPixels = async (filename) => {
    // console.log('Getting pixels for', filename)
    var {data, width, height} = await pixels(filename, {clip: { x: 49, y: 138, width: 1, height: 1 }})
    return data
}

const main = async () => {
    console.log("Main started")

    fs.readdir('target', (err, files) => {
        files.forEach(async f => {
            const filename = `target/${f}`
            let data = await getPixels(filename)
            if (false
                || equall(data, [ 99, 119, 142, 255 ])
                || equall(data, [ 250, 250, 250, 255 ])
                || equall(data, [ 192, 192, 192, 255 ])
            ) {
                fs.unlink(filename, () => {
                    console.log(f, 'removed')
                })
            }
        })
    })
}

const test = async () => {
    const users = [
        'shukshina411.jpg', // good
        'tarasovaanna_82.jpg', // bg
        'mmsi11042018.jpg', // gray
    ]

    users.forEach(async (f) => {
        const filename = `target/${f}`
        let data = await getPixels(filename)
        console.log(equall(data, [192, 192, 192, 255]))
    })
}

main()
// test()

