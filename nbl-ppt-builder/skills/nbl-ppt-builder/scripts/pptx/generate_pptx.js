/**
 * NBL PPT Builder - Generate PowerPoint from HTML slides
 *
 * Workflow:
 *   1. Collect all HTML pages (01_*.html, 02_*.html, ...)
 *   2. Create PptxGenJS presentation with 16:9 layout
 *   3. For each HTML page, call html2pptx() to convert to slide
 *   4. Save final .pptx file
 *
 * Usage:
 *   node generate_pptx.js /path/to/ppt/dir [output.pptx]
 *
 * Example:
 *   node generate_pptx.js /home/user/ppt_季度总结_20240131
 */

const path = require('path');
const fs = require('fs');
const pptxgen = require('pptxgenjs');
const html2pptx = require('./html2pptx');

// Constants
const SLIDE_WIDTH_IN = 10;
const SLIDE_HEIGHT_IN = 5.625; // 16:9 aspect ratio
const FILE_PATTERN = /^(\d{2,3})_.*\.html$/;

/**
 * Parse command line arguments
 */
function parseArgs(args) {
  const result = { checkMode: false, workDir: null, htmlFiles: [], outputFile: null };

  for (const arg of args) {
    if (arg === '--check' || arg === '--dry-run') {
      result.checkMode = true;
    } else if (arg.endsWith('.html')) {
      result.htmlFiles.push(arg);
    } else if (!result.workDir) {
      result.workDir = arg;
    } else if (!result.outputFile) {
      result.outputFile = arg;
    }
  }

  return result;
}

/**
 * Collect all HTML slide files from directory
 */
function collectSlides(workDir) {
  const files = fs.readdirSync(workDir);
  const slides = [];

  for (const file of files) {
    const match = file.match(FILE_PATTERN);
    if (!match) continue;

    const pageNum = parseInt(match[1], 10);
    const filePath = path.join(workDir, file);

    slides.push({ pageNum, file, path: filePath });
  }

  // Sort by page number
  slides.sort((a, b) => a.pageNum - b.pageNum);

  return slides;
}

/**
 * Check multiple HTML files
 */
async function checkFiles(htmlFiles) {
  const fileCount = htmlFiles.length;
  console.log(`\n📊 NBL PPT Builder - ${fileCount === 1 ? '单文件' : '多文件'}检测模式\n`);

  // Validate all files exist
  for (const htmlFile of htmlFiles) {
    if (!fs.existsSync(htmlFile)) {
      throw new Error(`File not found: ${htmlFile}`);
    }
  }

  // Create presentation for validation
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  pptx.author = 'NBL PPT Builder';
  pptx.title = 'NBL PPT Validation';

  console.log(`🔍 Checking ${fileCount} file(s) for validation errors...\n`);

  let checkErrors = [];

  for (const htmlFile of htmlFiles) {
    const fileName = path.basename(htmlFile);
    process.stdout.write(`   📄 Checking ${fileName}... `);

    try {
      await html2pptx(htmlFile, pptx, { checkMode: true });
      console.log('✅');
    } catch (error) {
      console.log('❌');
      checkErrors.push({ slide: fileName, error: error.message });
    }
  }

  console.log(`\n📋 检测结果:`);
  if (checkErrors.length === 0) {
    console.log(`   ✅ 所有 ${fileCount} 个页面检测通过，可以安全转换`);
    if (fileCount === 1) {
      console.log(`\n💡 提示: 该文件符合 PPT 生成要求`);
    }
  } else {
    console.log(`   ❌ 发现 ${checkErrors.length} 个问题:\n`);
    checkErrors.forEach((e, i) => {
      console.log(`   ${i + 1}. ${e.slide}`);
      console.log(`      ${e.error}\n`);
    });
    console.log(`💡 提示: 请先修复上述问题后再生成 PPT`);
    process.exit(1);
  }
}

/**
 * Main generation function
 */
async function generatePPTX(workDir, outputFile = 'presentation.pptx', checkMode = false) {
  const mode = checkMode ? '检测模式' : '生成模式';
  console.log(`\n📊 NBL PPT Builder - ${mode}\n`);

  // Validate work directory
  if (!fs.existsSync(workDir)) {
    throw new Error(`Work directory not found: ${workDir}`);
  }

  const slides = collectSlides(workDir);
  if (slides.length === 0) {
    throw new Error(`No slide files found in ${workDir}. Files must match pattern: 01_*.html`);
  }

  console.log(`📁 Found ${slides.length} slide(s):`);
  slides.forEach((slide, idx) => {
    console.log(`   ${idx + 1}. ${slide.file}`);
  });

  if (checkMode) {
    console.log(`\n🔍 Checking slides for validation errors...`);
  } else {
    console.log(`\n🔄 Converting slides to PowerPoint...`);
  }

  // Create presentation (even in check mode, needed for validation)
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  pptx.author = 'NBL PPT Builder';
  pptx.title = path.basename(workDir);

  let checkErrors = [];

  // Convert each slide
  for (const slide of slides) {
    process.stdout.write(`   📄 ${checkMode ? 'Checking' : 'Converting'} ${slide.file}... `);

    try {
      const result = await html2pptx(slide.path, pptx, { checkMode });

      if (checkMode) {
        // In check mode, collect validation errors but don't output file
        console.log('✅');
      } else {
        console.log('✅');
      }
    } catch (error) {
      console.log('❌');
      if (checkMode) {
        // In check mode, collect errors but continue checking other slides
        checkErrors.push({ slide: slide.file, error: error.message });
      } else {
        // In generation mode, fail immediately
        throw new Error(`Failed to convert ${slide.file}: ${error.message}`);
      }
    }
  }

  if (checkMode) {
    console.log(`\n📋 检测结果:`);
    if (checkErrors.length === 0) {
      console.log(`   ✅ 所有 ${slides.length} 个页面检测通过，可以安全生成 PPT`);
      console.log(`\n💡 提示: 使用以下命令生成 PPT 文件:`);
      console.log(`   node generate_pptx.js "${workDir}" "${outputFile}"`);
    } else {
      console.log(`   ❌ 发现 ${checkErrors.length} 个问题:\n`);
      checkErrors.forEach((e, i) => {
        console.log(`   ${i + 1}. ${e.slide}`);
        console.log(`      ${e.error}\n`);
      });
      console.log(`💡 提示: 请先修复上述问题后再生成 PPT`);
      process.exit(1);
    }
  } else {
    console.log(`\n💾 Saving to ${outputFile}...`);
    await pptx.writeFile({ fileName: outputFile });

    console.log(`\n✨ Done! ${slides.length} slides saved to ${outputFile}\n`);
  }

  return checkMode ? null : outputFile;
}

// CLI interface
const args = process.argv.slice(2);

if (args.length < 1 || args.includes('--help') || args.includes('-h')) {
  console.error(`
NBL PPT Builder - Generate PowerPoint from HTML slides

Usage:
  检测模式（推荐先执行）:
    node generate_pptx.js --check <work_dir>

  检测多个指定页面:
    node generate_pptx.js --check <page1.html> [page2.html] [page3.html]

  生成模式（检测通过后执行）:
    node generate_pptx.js <work_dir> [output_file]

Options:
  --check, --dry-run    检测模式：只检查不生成，报告所有问题
  --help, -h           显示帮助信息

Examples:
  1. 检测所有页面:
     node generate_pptx.js --check /path/to/ppt_季度总结_20240131

  2. 检测单个页面:
     node generate_pptx.js --check /path/to/ppt_季度总结_20240131/03_背景介绍.html

  3. 检测多个指定页面:
     node generate_pptx.js --check 03_背景.html 04_问题.html 05_方案.html

  4. 生成 PPT 文件:
     node generate_pptx.js /path/to/ppt_季度总结_20240131

  5. 生成并指定输出文件名:
     node generate_pptx.js /path/to/ppt_季度总结_20240131 quarterly_report.pptx
  `);
  process.exit(1);
}

const { checkMode, workDir, htmlFiles, outputFile } = parseArgs(args);

// File check mode (single or multiple)
if (htmlFiles.length > 0 && !workDir) {
  checkFiles(htmlFiles)
    .then(() => process.exit(0))
    .catch(error => {
      console.error(`\n❌ Error: ${error.message}\n`);
      process.exit(1);
    });
} else {
  // Directory mode (check or generate)
  generatePPTX(workDir, outputFile || 'presentation.pptx', checkMode)
    .then(() => process.exit(0))
    .catch(error => {
      console.error(`\n❌ Error: ${error.message}\n`);
      process.exit(1);
    });
}

module.exports = { generatePPTX, collectSlides };