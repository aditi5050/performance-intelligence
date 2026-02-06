import lighthouse from 'lighthouse';
import { launch } from 'chrome-launcher';

const url = process.argv[2];

async function runAudit() {

    const chrome = await launch({ chromeFlags: ['--headless'] });

    const options = {
        logLevel: 'silent',
        output: 'json',
        port: chrome.port,
    };

    const runnerResult = await lighthouse(url, options);

    const audits = runnerResult.lhr.audits;

    const result = {
        performance_score: runnerResult.lhr.categories.performance.score * 100,
        lcp: audits['largest-contentful-paint'].numericValue,
        cls: audits['cumulative-layout-shift'].numericValue,
        tbt: audits['total-blocking-time'].numericValue
    };

    // VERY IMPORTANT → output ONLY JSON
    console.log(JSON.stringify(result));

    await chrome.kill();
}

runAudit();
