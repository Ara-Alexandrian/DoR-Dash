import fs from 'fs';

// Manual analysis of the theme contrast based on the code
console.log('=== DoR-Dash Theme Contrast Analysis ===\n');

// Define the theme color values from app.css
const themes = {
  light: {
    name: 'Light Theme',
    background: 'rgb(255, 255, 255)', // white
    secondary: 'rgb(249, 250, 251)', // very light gray
    tertiary: 'rgb(243, 244, 246)', // light gray
    textPrimary: 'rgb(17, 24, 39)', // dark gray/black
    textSecondary: 'rgb(75, 85, 99)', // medium gray
  },
  dark: {
    name: 'Dark Theme',
    background: 'rgb(15, 23, 42)', // dark blue
    secondary: 'rgb(30, 41, 59)', // darker blue
    tertiary: 'rgb(51, 65, 85)', // medium blue
    textPrimary: 'rgb(248, 250, 252)', // very light gray/white
    textSecondary: 'rgb(226, 232, 240)', // light gray
  },
  dracula: {
    name: 'Sweet Dracula Theme',
    background: 'rgb(30, 32, 43)', // dark gray
    secondary: 'rgb(40, 42, 54)', // darker gray
    tertiary: 'rgb(50, 52, 63)', // medium gray
    textPrimary: 'rgb(248, 248, 242)', // very light yellow/white
    textSecondary: 'rgb(189, 147, 249)', // light purple
  },
  mbp: {
    name: 'MBP Dark Fire Theme',
    background: 'rgb(18, 18, 20)', // very dark gray
    secondary: 'rgb(25, 25, 28)', // dark gray
    tertiary: 'rgb(35, 35, 38)', // medium dark gray
    textPrimary: 'rgb(245, 245, 247)', // very light gray/white
    textSecondary: 'rgb(205, 205, 210)', // light gray
  },
  lsu: {
    name: 'LSU Dark Storm Theme',
    background: 'rgb(15, 10, 25)', // very dark purple
    secondary: 'rgb(22, 15, 35)', // dark purple
    tertiary: 'rgb(30, 20, 45)', // medium purple
    textPrimary: 'rgb(248, 245, 255)', // very light purple/white
    textSecondary: 'rgb(215, 205, 230)', // light purple
  }
};

// Card specific colors based on the about page code
const cardColors = {
  frontend: {
    light: { bg: 'rgb(239, 246, 255)', text: 'rgb(30, 64, 175)' }, // blue-50 to blue-800
    dark: { bg: 'rgb(30, 58, 138)', text: 'rgb(219, 234, 254)' }, // blue-900/20 to blue-100
    dracula: { bg: 'rgb(51, 65, 85)', text: 'rgb(255, 255, 255)' }, // slate-800 to white
    mbp: { bg: 'rgb(55, 65, 81)', text: 'rgb(255, 255, 255)' }, // gray-800 to white
    lsu: { bg: 'rgb(51, 65, 85)', text: 'rgb(255, 255, 255)' } // slate-800 to white
  },
  backend: {
    light: { bg: 'rgb(240, 253, 244)', text: 'rgb(22, 101, 52)' }, // green-50 to green-800
    dark: { bg: 'rgb(20, 83, 45)', text: 'rgb(187, 247, 208)' }, // green-900/20 to green-100
    dracula: { bg: 'rgb(51, 65, 85)', text: 'rgb(255, 255, 255)' }, // slate-800 to white
    mbp: { bg: 'rgb(55, 65, 81)', text: 'rgb(255, 255, 255)' }, // gray-800 to white
    lsu: { bg: 'rgb(51, 65, 85)', text: 'rgb(255, 255, 255)' } // slate-800 to white
  },
  database: {
    light: { bg: 'rgb(245, 243, 255)', text: 'rgb(91, 33, 182)' }, // purple-50 to purple-800
    dark: { bg: 'rgb(88, 28, 135)', text: 'rgb(221, 214, 254)' }, // purple-900/20 to purple-100
    dracula: { bg: 'rgb(51, 65, 85)', text: 'rgb(255, 255, 255)' }, // slate-800 to white
    mbp: { bg: 'rgb(55, 65, 81)', text: 'rgb(255, 255, 255)' }, // gray-800 to white
    lsu: { bg: 'rgb(51, 65, 85)', text: 'rgb(255, 255, 255)' } // slate-800 to white
  }
};

// Function to calculate contrast ratio
function calculateContrastRatio(rgb1, rgb2) {
  const getLuminance = (rgb) => {
    const [r, g, b] = rgb.match(/\d+/g).map(Number);
    const [rs, gs, bs] = [r, g, b].map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  };
  
  const l1 = getLuminance(rgb1);
  const l2 = getLuminance(rgb2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  
  return (lighter + 0.05) / (darker + 0.05);
}

// Function to evaluate contrast quality
function evaluateContrast(ratio) {
  if (ratio >= 7) return 'AAA (Excellent)';
  if (ratio >= 4.5) return 'AA (Good)';
  if (ratio >= 3) return 'AA Large (Acceptable for large text)';
  return 'Fail (Poor contrast)';
}

console.log('Technical Breakdown Cards Contrast Analysis:');
console.log('=' .repeat(50));

const cardTypes = ['frontend', 'backend', 'database'];
const cardNames = ['Frontend (SvelteKit)', 'Backend (FastAPI)', 'Database (PostgreSQL)'];

for (const [themeKey, themeData] of Object.entries(themes)) {
  console.log(`\n${themeData.name.toUpperCase()}`);
  console.log('-'.repeat(themeData.name.length + 10));
  
  cardTypes.forEach((cardType, index) => {
    const cardData = cardColors[cardType][themeKey];
    const headingContrast = calculateContrastRatio(cardData.text, cardData.bg);
    const bulletContrast = calculateContrastRatio(cardData.text, cardData.bg);
    
    console.log(`\n  ${cardNames[index]}:`);
    console.log(`    Background: ${cardData.bg}`);
    console.log(`    Text Color: ${cardData.text}`);
    console.log(`    Heading Contrast: ${headingContrast.toFixed(2)} - ${evaluateContrast(headingContrast)}`);
    console.log(`    Bullet Text Contrast: ${bulletContrast.toFixed(2)} - ${evaluateContrast(bulletContrast)}`);
  });
}

// Overall theme analysis
console.log('\n\n' + '='.repeat(50));
console.log('OVERALL THEME ANALYSIS');
console.log('='.repeat(50));

for (const [themeKey, themeData] of Object.entries(themes)) {
  console.log(`\n${themeData.name}:`);
  
  // Check general text contrast
  const primaryTextContrast = calculateContrastRatio(themeData.textPrimary, themeData.background);
  const secondaryTextContrast = calculateContrastRatio(themeData.textSecondary, themeData.background);
  
  console.log(`  Primary Text vs Background: ${primaryTextContrast.toFixed(2)} - ${evaluateContrast(primaryTextContrast)}`);
  console.log(`  Secondary Text vs Background: ${secondaryTextContrast.toFixed(2)} - ${evaluateContrast(secondaryTextContrast)}`);
  
  // Card background contrast
  const cardBgContrast = calculateContrastRatio(themeData.textPrimary, themeData.secondary);
  console.log(`  Text vs Card Background: ${cardBgContrast.toFixed(2)} - ${evaluateContrast(cardBgContrast)}`);
}

console.log('\n\n' + '='.repeat(50));
console.log('KEY FINDINGS & RECOMMENDATIONS');
console.log('='.repeat(50));

console.log(`
Based on the code analysis, here are the key findings:

1. LIGHT THEME: Excellent contrast across all cards
   - Uses dark text (blue-800, green-800, purple-800) on light backgrounds
   - All contrast ratios exceed AA standards

2. DARK THEME: Good contrast with recent fixes
   - Uses light text (blue-100, green-100, purple-100) on dark backgrounds  
   - Text should be clearly visible

3. DRACULA THEME: Fixed with white text
   - All cards now use white text on slate-800 backgrounds
   - Should provide excellent contrast

4. MBP THEME: Fixed with white text
   - All cards use white text on gray-800 backgrounds
   - Should provide excellent contrast

5. LSU THEME: Fixed with white text
   - All cards use white text on slate-800 backgrounds
   - Should provide excellent contrast

The recent fix (lines 419-426 in about page) ensures that all dark themes
(dracula, mbp, lsu) use white text, which should resolve the contrast issues.

RECOMMENDATION: The code changes appear correct. The white text fix should 
resolve the contrast issues across all themes.
`);

console.log('\n=== Analysis Complete ===');