import fetch from 'node-fetch';
import { JSDOM } from 'jsdom';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const themes = ['light', 'dark', 'dracula', 'mbp', 'lsu'];
const pages = ['/about', '/logout'];
const baseUrl = 'https://dd.kronisto.net';

// Theme CSS rules based on the application's theme system
const themeColors = {
    light: {
        background: '#ffffff',
        text: '#333333',
        cardBg: '#f8f9fa',
        cardText: '#333333'
    },
    dark: {
        background: '#1a1a1a',
        text: '#e0e0e0',
        cardBg: '#2d2d2d',
        cardText: '#e0e0e0'
    },
    dracula: {
        background: '#282a36',
        text: '#f8f8f2',
        cardBg: '#44475a',
        cardText: '#f8f8f2'
    },
    mbp: {
        background: '#0d1117',
        text: '#c9d1d9',
        cardBg: '#161b22',
        cardText: '#c9d1d9'
    },
    lsu: {
        background: '#461d7c',
        text: '#ffffff',
        cardBg: '#5a2a8f',
        cardText: '#ffffff'
    }
};

function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

function getLuminance(color) {
    const rgb = hexToRgb(color);
    if (!rgb) return 0;
    
    const sRGB = [rgb.r, rgb.g, rgb.b].map(val => {
        val = val / 255;
        return val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4);
    });
    
    return 0.2126 * sRGB[0] + 0.7152 * sRGB[1] + 0.0722 * sRGB[2];
}

function getContrastRatio(color1, color2) {
    const lum1 = getLuminance(color1);
    const lum2 = getLuminance(color2);
    const lighter = Math.max(lum1, lum2);
    const darker = Math.min(lum1, lum2);
    return (lighter + 0.05) / (darker + 0.05);
}

async function analyzePage(url, theme) {
    try {
        const response = await fetch(url);
        const html = await response.text();
        const dom = new JSDOM(html);
        const document = dom.window.document;
        
        const colors = themeColors[theme];
        const analysis = {
            theme,
            url,
            mainContrast: getContrastRatio(colors.background, colors.text),
            cardContrast: getContrastRatio(colors.cardBg, colors.cardText),
            elements: []
        };
        
        // Count cards
        const cards = document.querySelectorAll('.card, .about-card, [class*="card"]');
        analysis.cardCount = cards.length;
        
        // Count H4 headings
        const h4s = document.querySelectorAll('h4');
        analysis.h4Count = h4s.length;
        analysis.h4Texts = Array.from(h4s).map(h4 => h4.textContent.trim());
        
        // Check for specific elements on the about page
        if (url.includes('/about')) {
            const sections = document.querySelectorAll('.about-section, .content-section');
            analysis.sectionCount = sections.length;
        }
        
        return analysis;
    } catch (error) {
        return { error: error.message, theme, url };
    }
}

async function runAnalysis() {
    const results = [];
    
    for (const theme of themes) {
        for (const page of pages) {
            console.log(`Analyzing ${theme} theme on ${page} page...`);
            const analysis = await analyzePage(`${baseUrl}${page}`, theme);
            results.push(analysis);
        }
    }
    
    // Generate report
    let report = '# DoR-Dash Theme Color Analysis Report\n\n';
    report += `Generated on: ${new Date().toISOString()}\n\n`;
    report += '## Color Contrast Analysis\n\n';
    
    for (const theme of themes) {
        const colors = themeColors[theme];
        report += `### ${theme.toUpperCase()} Theme\n\n`;
        report += `- **Background:** ${colors.background}\n`;
        report += `- **Text:** ${colors.text}\n`;
        report += `- **Main Contrast Ratio:** ${getContrastRatio(colors.background, colors.text).toFixed(2)} ${getContrastRatio(colors.background, colors.text) >= 4.5 ? '✅' : '❌'}\n`;
        report += `- **Card Background:** ${colors.cardBg}\n`;
        report += `- **Card Text:** ${colors.cardText}\n`;
        report += `- **Card Contrast Ratio:** ${getContrastRatio(colors.cardBg, colors.cardText).toFixed(2)} ${getContrastRatio(colors.cardBg, colors.cardText) >= 4.5 ? '✅' : '❌'}\n\n`;
        
        for (const page of pages) {
            const result = results.find(r => r.theme === theme && r.url && r.url.endsWith(page));
            if (result && !result.error) {
                report += `#### ${page} Page\n`;
                report += `- Cards found: ${result.cardCount || 0}\n`;
                report += `- H4 headings found: ${result.h4Count || 0}\n`;
                if (result.h4Texts && result.h4Texts.length > 0) {
                    report += `- H4 texts: ${result.h4Texts.map(t => `"${t}"`).join(', ')}\n`;
                }
                if (result.sectionCount !== undefined) {
                    report += `- Sections found: ${result.sectionCount}\n`;
                }
                report += '\n';
            }
        }
    }
    
    // Summary
    report += '## Summary of Issues\n\n';
    
    let issueCount = 0;
    for (const theme of themes) {
        const colors = themeColors[theme];
        const mainContrast = getContrastRatio(colors.background, colors.text);
        const cardContrast = getContrastRatio(colors.cardBg, colors.cardText);
        
        if (mainContrast < 4.5) {
            report += `- ❌ **${theme}** theme: Main text contrast ratio (${mainContrast.toFixed(2)}) is below WCAG AA standard (4.5)\n`;
            issueCount++;
        }
        
        if (cardContrast < 4.5) {
            report += `- ❌ **${theme}** theme: Card text contrast ratio (${cardContrast.toFixed(2)}) is below WCAG AA standard (4.5)\n`;
            issueCount++;
        }
        
        if (mainContrast < 3) {
            report += `- 🚨 **${theme}** theme: Main text contrast ratio (${mainContrast.toFixed(2)}) is severely low\n`;
            issueCount++;
        }
    }
    
    if (issueCount === 0) {
        report += '✅ All themes have acceptable contrast ratios!\n';
    }
    
    report += '\n## Recommendations\n\n';
    report += '1. **Text Readability:** Ensure all text has a contrast ratio of at least 4.5:1 against its background\n';
    report += '2. **Card Visibility:** Cards should have distinct borders or shadows if their background is similar to the page background\n';
    report += '3. **H4 Headings:** Headings should have sufficient weight and contrast to stand out from body text\n';
    report += '4. **Theme Consistency:** Ensure all UI elements respect the current theme selection\n';
    
    await fs.writeFile(path.join(__dirname, 'theme-analysis-report.md'), report);
    console.log('\nTheme analysis report generated: theme-analysis-report.md');
    
    return results;
}

// Check if we have the required dependencies
import('node-fetch').catch(() => {
    console.error('node-fetch is not installed. Installing...');
    process.exit(1);
});

import('jsdom').catch(() => {
    console.error('jsdom is not installed. Installing...');
    process.exit(1);
});

// Run the analysis
runAnalysis().catch(console.error);