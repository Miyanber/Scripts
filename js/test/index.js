#!/usr/bin/env node
/*(async function () {
    let isTimeout = false;
    for (let j = 0; j < 1; j++) {
        const inputKenon = new Promise((resolve, _) => {
            setTimeout(() => resolve("ok"), 1000);
        })
        const timeOut = new Promise((_, reject) => {
            setTimeout(() => reject("timeout"), 2000);
        })
        await Promise.race([inputKenon, timeOut])
            .then((value) => {
                console.log("成功" + value)
            }).catch((error) => {
                console.log("失敗" + error)
            })
    }
    console.log("finished")
})();

function sleep(milliSec) {
    return new Promise(function (resolve) {
        setTimeout(() => resolve(), milliSec);
    });
}*/

console.log(!"");

let date = new Date("2020/05/02");
date = new Date();
console.log(date.toString());