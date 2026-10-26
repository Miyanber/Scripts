#!/usr/bin/env node
const { chromium } = require('playwright-chromium');

const url = "https://www.jr-odekake.net/goyoyaku/campaign/sunriseseto_izumo/form.html";

async function sleep(millSec = 1000) {
    return new Promise((resolve) => setTimeout(() => resolve(), millSec));
};

function zeroPadding(num) {
    const string = ("00" + num);
    return string.substring(string.length - 2, string.length);
}

/**
 * 
 * @param {import('playwright-chromium').Page} page 
 */
async function loadFont(page) {
    page.evaluate(() => {
        document.head.insertAdjacentHTML("beforeend", `
            <style>* {font-family: "Noto Sans JP", sans-serif; }</style>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@100..900&display=swap" rel="stylesheet">`);
    })
}

/**
 * 
 * @param {import("playwright-chromium").Page} page 
 * @param {InvocationContext} context
 * @param {String} locateDate "09" など
 * @param {String} trainType "seto" or "izumo"
 * @param {String} seatType "普通車ノビノビ座席" など
 * @returns メンテナンス時はfalseを返す。
 */
async function initPage(page, context, locateDate, trainType, seatType) {
    try {
        await page.goto(url);
        await page.locator(`//html/body/div[1]/div/div/div/main/div/div/section/form/ul/li[2]/button`).click();// 会員ログインせずに予約
        await sleep(500);
        await page.locator(`//*[@id="jsSelectMonth"]`).selectOption("03");//3月固定
        await page.locator(`//*[@id="jsSelectDay"]`).selectOption(locateDate);//日付
        await page.locator(`//*[@id="jsSelectHour"]`).selectOption("00");//時間
        await page.locator(`//*[@id="jsSelectMinute"]`).selectOption("00");//分
        await page.locator(`//*[@id="jsSelectTrainType"]`).selectOption(trainType);
        await page.locator(`//*[@id="inputDepartStName"]`).selectOption("%91%E5%8D%E3");//大阪
        await page.locator(`//*[@id="inputArriveStName"]`).selectOption("%93%8C%8B%9E");//東京
        await page.locator(`//*[@id="jsCheckBox_west"]`).check();//大阪選択時のチェックボックス
        await page.locator(`input[value=${seatType}]`).check();//設備の種類の選択ラジオボタン
        await sleep(500);
        await page.locator(`//*[@id="submitButton"]`).click();//送信ボタンを押す
        const date = await (await page.waitForSelector("//html/body/main/section[2]/section[1]/div/ul/li[1]/span[1]/em[2]")).textContent();
        if (date != locateDate) {
            context.warn("検索結果の日付が一致しません。再実行します。");
            context.warn("locateDate:", locateDate, "date(browser):", date);
            initPage(page, context, locateDate, trainType, seatType);
        }
    } catch (e) {
        context.log("エラー内容:", e);
        context.log("locateDate:", locateDate);
        await loadFont(page);
        const error_message = await page.locator(`//*[@id="top"]/main/section/div[2]`).textContent();
        if (error_message.includes("メンテナンス")) {
            context.log("メンテナンス中のため、終了します。");
            return false;
        } else if (error_message.includes("混雑中")) {
            context.log("混雑中のため、再実行します。");
            return await initPage(page, context, locateDate, trainType, seatType);
        } else {
            throw new Error(`原因不明のエラーです。エラー内容： ${e}`);
        }
    }
    await loadFont(page);
    return true
}

function getCssPath(nth) {
    return `table.seat-facility > tbody > tr > td:nth-of-type(${nth}) img`
}

/**
 * 
 * @param {import("playwright-chromium").Page} page 
 * @param {InvocationContext} context 
 * @param {Number} locateDateNumber 
 * @param {String} trainType
 * @returns メンテナンス時はnullを返す。
 */
async function getStatus(page, context, locateDateNumber, trainType) {
    const smoking = { "禁煙": "残席なし", "喫煙": "残席なし" }
    const result = {// 必ず（この場合はシャロ―でOK）コピーをすること！！！
        "普通車ノビノビ座席": { "禁煙": "残席なし" },
        "シングルデラックス": { ...smoking },
        "シングルツイン": { ...smoking },
        "シングル": { ...smoking },
        // "ソロ": { "禁煙": "残席なし"},
        "サンライズツイン": { ...smoking }
    }
    const locateDate = zeroPadding(locateDateNumber);
    let resultText;

    // ##### ノビノビ・シングルツイン・シングルデラックス #####
    if (!await initPage(page, context, locateDate, trainType, "普通車ノビノビ座席"))
        // メンテナンス時対応
        return null
    resultText = await page.locator("//html/body/main/section[2]/section[1]/div/div").textContent();
    if (resultText.includes("通常のきっぷのみの予約")) {
        result["普通車ノビノビ座席"]["禁煙"] = await page.locator(getCssPath(1)).getAttribute("alt");
        result["シングルツイン"]["禁煙"] = await page.locator(getCssPath(2)).getAttribute("alt");
        result["シングルツイン"]["喫煙"] = await page.locator(getCssPath(3)).getAttribute("alt");
        result["シングルデラックス"]["禁煙"] = await page.locator(getCssPath(4)).getAttribute("alt");
        result["シングルデラックス"]["喫煙"] = await page.locator(getCssPath(5)).getAttribute("alt");
        // await page.evaluate(() => {document.querySelector("table.seat-facility > tbody > tr > td:nth-of-type(2)").style.backgroundColor = "black"})
        // await page.evaluate(() => {document.querySelector("table.seat-facility > tbody > tr > td:nth-of-type(2)").style.backgroundColor = "red"})
        // await page.evaluate(() => {document.querySelector("table.seat-facility > tbody > tr > td:nth-of-type(3)").style.backgroundColor = "blue"})
        // await page.evaluate(() => {document.querySelector("table.seat-facility > tbody > tr > td:nth-of-type(4)").style.backgroundColor = "purple"})
        // await page.evaluate(() => {document.querySelector("table.seat-facility > tbody > tr > td:nth-of-type(5)").style.backgroundColor = "yellow"})
    }
    await page.screenshot({ path: `./screenshots/03${locateDate}_${trainType}_1.png`, fullPage: true, });

    // ##### サンライズツイン #####
    await initPage(page, context, locateDate, trainType, "サンライズツイン");
    resultText = await page.locator("//html/body/main/section[2]/section[1]/div/div").textContent();
    if (resultText.includes("通常のきっぷのみの予約")) {
        result["サンライズツイン"]["禁煙"] = await page.locator(getCssPath(1)).getAttribute("alt");
        result["サンライズツイン"]["喫煙"] = await page.locator(getCssPath(2)).getAttribute("alt");
    }
    await page.screenshot({ path: `./screenshots/03${locateDate}_${trainType}_2.png`, fullPage: true, });

    // ##### シングル #####
    await initPage(page, context, locateDate, trainType, "シングル");
    resultText = await page.locator("//html/body/main/section[2]/section[1]/div/div").textContent();
    if (resultText.includes("通常のきっぷのみの予約")) {
        result["シングル"]["禁煙"] = await page.locator(getCssPath(1)).getAttribute("alt");
        result["シングル"]["喫煙"] = await page.locator(getCssPath(2)).getAttribute("alt");
    }
    await page.screenshot({ path: `./screenshots/03${locateDate}_${trainType}_3.png`, fullPage: true, });

    return result;
}

async function httpFunction(locateDateNumber) {
    const context = console;
    // context.log(`Http function processed request for url "${request.url}"`);

    // ##### フォント読み込み(旧Ver)
    // const { promisify } = require("util");
    // const { fs } = require("node:fs/promises");
    // const { exec } = require("node:child_process");

    // const execAsync = promisify(exec);

    // const fontUpdate = async () => {
    //     const fontPath = process.env.FONT_PATH || "/home/.fonts";
    //     try {
    //         await fs.stat(fontPath);
    //         return;
    //     } catch { }

    //     // ln -s /home/site/wwwroot/fonts $FONT_PATH
    //     await execAsync(`ln -s /home/site/wwwroot/fonts ${fontPath}`);
    // };

    // await fontUpdate();
    // ##### 

    // let locateDate = request.query.get('date') || (await request.json()).date || 'world';
    let locateDate = locateDateNumber;
    // context.log(locateDate);
    locateDate = Number(locateDate);
    if (!locateDate) {
        context.log("パラメータが不正です。");
        throw new Error("Invalid Parameter [AutoReserve]");
    }

    const browser = await chromium.launch();
    const page_seto = await browser.newPage();
    const page_izumo = await browser.newPage();

    let response = {
        "瀬戸": null,
        "出雲": null,
    }

    const seto_promise = new Promise(async (resolve) => {
        response["瀬戸"] = await getStatus(page_seto, context, locateDate, "seto");
        resolve();
    });
    const izumo_promise = new Promise(async (resolve) => {
        response["出雲"] = await getStatus(page_izumo, context, locateDate, "izumo");
        resolve();
    })
    await Promise.all([seto_promise, izumo_promise]);
    // await seto_promise.then();
    // await izumo_promise.then();

    if (!response["瀬戸"]) {
        return {
            body: "Under Maintenance",
            status: 400,
        };
    }

    context.log(response);

    await page_seto.close();
    await page_izumo.close();
    await browser.close();

    return { jsonBody: response };
}

async function main() {
    const start = 15;
    const end = 31;
    const browser = await chromium.launch({
        channel: "chrome",
        // headless: false, //falseの場合はブラウザ上での動きを確認しながら実行可能
        devtools: true
    });
    const page = await browser.newPage();
    for (let locateDateNumber = start; locateDateNumber < end + 1; locateDateNumber++) {
        console.log(`日付：03/${zeroPadding(locateDateNumber)}`);
        await httpFunction(locateDateNumber);
    }
    await page.close();
    await browser.close();
}

main();