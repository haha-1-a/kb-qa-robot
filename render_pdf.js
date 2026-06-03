const { chromium } = require("playwright");
const path = require("path");

(async () => {
  const htmlPath = path.resolve("演讲讲义.html");
  const pdfPath = path.resolve("演讲讲义_企业知识库问答机器人.pdf");

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(`file://${htmlPath}`, { waitUntil: "networkidle" });

  await page.pdf({
    path: pdfPath,
    format: "A4",
    margin: { top: "2cm", bottom: "2cm", left: "2.2cm", right: "2.2cm" },
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: '<span style="font-size:10px;color:#888;font-family:sans-serif;text-align:center;width:100%;display:inline-block;">— <span class="pageNumber"></span> —</span>',
  });

  console.log(`PDF 已生成: ${path.basename(pdfPath)}`);
  await browser.close();
})();
