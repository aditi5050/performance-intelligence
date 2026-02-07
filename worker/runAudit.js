import lighthouse from "lighthouse";
import { launch } from "chrome-launcher";

const url = process.argv[2];

async function runAudit(){

 let chrome;

 try{

  chrome = await launch({
    chromeFlags:["--headless","--no-sandbox"]
  });

  const options={
    logLevel:"silent",
    output:"json",
    port:chrome.port
  };

  const runnerResult = await lighthouse(url,options);

  const audits = runnerResult.lhr.audits;

  const safe = (name)=>audits[name]?.numericValue || 0;
  const safeItems = (name)=>audits[name]?.details?.items || [];

  const result = {

    performance_score:
      (runnerResult.lhr.categories.performance.score || 0)*100,

    lcp: safe("largest-contentful-paint"),
    cls: safe("cumulative-layout-shift"),
    tbt: safe("total-blocking-time"),

    deep_audits:{
      render_blocking:safeItems("render-blocking-resources"),
      unused_css:safeItems("unused-css-rules"),
      unused_js:safeItems("unused-javascript"),
      lcp_element:safeItems("largest-contentful-paint-element")
    }

  };

  console.log(JSON.stringify(result));

 }catch(error){

   console.log(JSON.stringify({
     error:true,
     message:error.message
   }));

 }finally{

   if(chrome){
     await chrome.kill();
   }
 }
}

runAudit();
