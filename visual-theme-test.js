import puppeteer from 'puppeteer';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const themes = ['light', 'dark', 'dracula', 'mbp', 'lsu'];
const pages = ['/about', '/logout'];
const baseUrl = 'https://dd.kronisto.net';

async function setTheme(page, theme) {
    await page.evaluate((themeName) => {
        // Set the theme in localStorage
        localStorage.setItem('theme', themeName);
        
        // Update document classes
        document.documentElement.className = '';
        document.documentElement.classList.add(themeName);
        document.body.className = '';
        document.body.classList.add(themeName);
    }, theme);
}

async function analyzeVisualAppearance(page, theme, pageName) {
    const analysis = await page.evaluate(() => {
        const getComputedColor = (element, property) => {
            return window.getComputedStyle(element)[property];
        };

        const getLuminance = (color) => {
            // Convert color to RGB
            const rgb = color.match(/\d+/g);
            if (!rgb) return 0;
            const [r, g, b] = rgb.map(Number);
            
            // Calculate relative luminance
            const sRGB = [r, g, b].map(val => {
                val = val / 255;
                return val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4);
            });
            
            return 0.2126 * sRGB[0] + 0.7152 * sRGB[1] + 0.0722 * sRGB[2];
        };

        const getContrastRatio = (color1, color2) => {
            const lum1 = getLuminance(color1);
            const lum2 = getLuminance(color2);
            const lighter = Math.max(lum1, lum2);
            const darker = Math.min(lum1, lum2);
            return (lighter + 0.05) / (darker + 0.05);
        };

        const body = document.body;
        const backgroundColor = getComputedColor(body, 'backgroundColor');
        const textColor = getComputedColor(body, 'color');
        
        const results = {
            backgroundColor,
            textColor,
            bodyContrastRatio: getContrastRatio(backgroundColor, textColor),
            elements: []
        };

        // Check cards on about page
        const cards = document.querySelectorAll('.card, .about-card, [class*="card"]');
        cards.forEach((card, index) => {
            const cardBg = getComputedColor(card, 'backgroundColor');
            const cardText = getComputedColor(card, 'color');
            results.elements.push({
                type: 'card',
                index,
                backgroundColor: cardBg,
                textColor: cardText,
                contrastRatio: getContrastRatio(cardBg, cardText),
                visible: card.offsetHeight > 0 && card.offsetWidth > 0
            });
        });

        // Check H4 headings
        const h4s = document.querySelectorAll('h4');
        h4s.forEach((h4, index) => {
            const h4Color = getComputedColor(h4, 'color');
            const h4Bg = getComputedColor(h4.parentElement, 'backgroundColor');
            results.elements.push({
                type: 'h4',
                index,
                text: h4.textContent.trim(),
                color: h4Color,
                backgroundColor: h4Bg,
                contrastRatio: getContrastRatio(h4Bg, h4Color),
                visible: h4.offsetHeight > 0 && h4.offsetWidth > 0
            });
        });

        // Check all text elements
        const textElements = document.querySelectorAll('p, span, div, a, button, label');
        let lowContrastCount = 0;
        textElements.forEach(el => {
            if (el.textContent.trim()) {
                const elColor = getComputedColor(el, 'color');
                const elBg = getComputedColor(el, 'backgroundColor');
                const contrast = getContrastRatio(elBg, elColor);
                if (contrast < 4.5) { // WCAG AA standard
                    lowContrastCount++;
                }
            }
        });
        results.lowContrastElements = lowContrastCount;

        return results;
    });

    return analysis;
}

async function runTests() {
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const results = [];
    const screenshotDir = path.join(__dirname, 'visual-test-screenshots');
    await fs.mkdir(screenshotDir, { recursive: true });

    for (const theme of themes) {
        for (const pagePath of pages) {
            console.log(`Testing ${theme} theme on ${pagePath} page...`);
            
            const page = await browser.newPage();
            await page.setViewport({ width: 1280, height: 800 });
            
            try {
                // Navigate to the page
                await page.goto(`${baseUrl}${pagePath}`, { waitUntil: 'networkidle2' });
                
                // Set the theme
                await setTheme(page, theme);
                
                // Wait for theme to apply
                await page.waitForTimeout(500);
                
                // Take screenshot
                const screenshotPath = path.join(screenshotDir, `${theme}-${pagePath.replace('/', '')}.png`);
                await page.screenshot({ path: screenshotPath, fullPage: true });
                
                // Analyze visual appearance
                const analysis = await analyzeVisualAppearance(page, theme, pagePath);
                
                results.push({
                    theme,
                    page: pagePath,
                    screenshot: screenshotPath,
                    analysis
                });
                
            } catch (error) {
                console.error(`Error testing ${theme} on ${pagePath}:`, error);
                results.push({
                    theme,
                    page: pagePath,
                    error: error.message
                });
            }
            
            await page.close();
        }
    }

    await browser.close();
    
    // Generate report
    const report = generateReport(results);
    await fs.writeFile(path.join(__dirname, 'visual-test-report.md'), report);
    console.log('\nVisual test report generated: visual-test-report.md');
    
    return results;
}

function generateReport(results) {
    let report = '# DoR-Dash Visual Theme Testing Report\n\n';
    report += `Generated on: ${new Date().toISOString()}\n\n`;
    
    for (const theme of themes) {
        report += `## ${theme.toUpperCase()} Theme\n\n`;
        
        for (const pagePath of pages) {
            const result = results.find(r => r.theme === theme && r.page === pagePath);
            if (!result) continue;
            
            report += `### ${pagePath} Page\n\n`;
            
            if (result.error) {
                report += `**Error:** ${result.error}\n\n`;
                continue;
            }
            
            const analysis = result.analysis;
            report += `- **Background Color:** ${analysis.backgroundColor}\n`;
            report += `- **Text Color:** ${analysis.textColor}\n`;
            report += `- **Main Contrast Ratio:** ${analysis.bodyContrastRatio.toFixed(2)} ${analysis.bodyContrastRatio >= 4.5 ? '✅' : '❌'}\n`;
            report += `- **Low Contrast Elements:** ${analysis.lowContrastElements}\n\n`;
            
            // Report on cards
            const cards = analysis.elements.filter(el => el.type === 'card');
            if (cards.length > 0) {
                report += `**Cards (${cards.length} found):**\n`;
                cards.forEach((card, i) => {
                    report += `- Card ${i + 1}: ${card.visible ? 'Visible' : 'Hidden'}, Contrast: ${card.contrastRatio.toFixed(2)} ${card.contrastRatio >= 4.5 ? '✅' : '❌'}\n`;
                });
                report += '\n';
            }
            
            // Report on H4 headings
            const h4s = analysis.elements.filter(el => el.type === 'h4');
            if (h4s.length > 0) {
                report += `**H4 Headings (${h4s.length} found):**\n`;
                h4s.forEach(h4 => {
                    report += `- "${h4.text}": ${h4.visible ? 'Visible' : 'Hidden'}, Contrast: ${h4.contrastRatio.toFixed(2)} ${h4.contrastRatio >= 4.5 ? '✅' : '❌'}\n`;
                });
                report += '\n';
            }
            
            report += `**Screenshot:** ${result.screenshot}\n\n`;
        }
    }
    
    // Summary
    report += '## Summary\n\n';
    report += '### Issues Found:\n\n';
    
    let issueCount = 0;
    for (const result of results) {
        if (result.error) {
            report += `- ❌ Error on ${result.theme} theme, ${result.page} page: ${result.error}\n`;
            issueCount++;
            continue;
        }
        
        const analysis = result.analysis;
        if (analysis.bodyContrastRatio < 4.5) {
            report += `- ❌ Low main contrast on ${result.theme} theme, ${result.page} page (${analysis.bodyContrastRatio.toFixed(2)})\n`;
            issueCount++;
        }
        
        if (analysis.lowContrastElements > 5) {
            report += `- ⚠️  ${analysis.lowContrastElements} low contrast elements on ${result.theme} theme, ${result.page} page\n`;
            issueCount++;
        }
        
        const lowContrastCards = analysis.elements.filter(el => el.type === 'card' && el.contrastRatio < 4.5);
        if (lowContrastCards.length > 0) {
            report += `- ❌ ${lowContrastCards.length} cards with low contrast on ${result.theme} theme, ${result.page} page\n`;
            issueCount++;
        }
        
        const hiddenCards = analysis.elements.filter(el => el.type === 'card' && !el.visible);
        if (hiddenCards.length > 0) {
            report += `- ⚠️  ${hiddenCards.length} hidden cards on ${result.theme} theme, ${result.page} page\n`;
            issueCount++;
        }
        
        const lowContrastH4s = analysis.elements.filter(el => el.type === 'h4' && el.contrastRatio < 4.5);
        if (lowContrastH4s.length > 0) {
            report += `- ❌ ${lowContrastH4s.length} H4 headings with low contrast on ${result.theme} theme, ${result.page} page\n`;
            issueCount++;
        }
    }
    
    if (issueCount === 0) {
        report += '✅ No major issues found!\n';
    }
    
    return report;
}

// Run the tests
runTests().catch(console.error);