import https from 'https';

console.log('=== Live Site Theme Test ===\n');

// Function to fetch page content
function fetchPage(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

try {
  console.log('Fetching DoR-Dash about page...');
  const html = await fetchPage('https://dd.kronisto.net/about');
  
  console.log('✅ Successfully fetched the page');
  console.log(`📄 Page size: ${html.length} characters\n`);
  
  // Check if the theme system is in place
  const hasThemeScript = html.includes('localStorage.getItem(\'theme\')');
  console.log(`🎨 Theme system detected: ${hasThemeScript ? '✅ Yes' : '❌ No'}`);
  
  // Check for the specific theme classes we're testing
  const themes = ['light', 'dark', 'dracula', 'mbp', 'lsu'];
  console.log('\n🔍 Theme availability check:');
  themes.forEach(theme => {
    const hasTheme = html.includes(theme);
    console.log(`   ${theme}: ${hasTheme ? '✅' : '❌'}`);
  });
  
  // Check for the technical breakdown cards section
  const hasCards = html.includes('Frontend (SvelteKit)') && 
                   html.includes('Backend (FastAPI)') && 
                   html.includes('Database (PostgreSQL)');
  console.log(`\n📊 Technical breakdown cards found: ${hasCards ? '✅ Yes' : '❌ No'}`);
  
  // Check for the specific white text fix in dark themes
  const hasWhiteTextFix = html.includes('dracula:text-white') && 
                          html.includes('mbp:text-white') && 
                          html.includes('lsu:text-white');
  console.log(`🔧 White text fix applied: ${hasWhiteTextFix ? '✅ Yes' : '❌ No'}`);
  
  // Check for CSS classes that indicate the theme-aware styling
  const hasTailwindThemes = html.includes('dark:from-') && 
                           html.includes('dracula:from-') && 
                           html.includes('mbp:from-');
  console.log(`🎭 Tailwind theme classes found: ${hasTailwindThemes ? '✅ Yes' : '❌ No'}`);
  
  console.log('\n📋 Analysis Summary:');
  console.log('==================');
  
  if (hasThemeScript && hasCards && hasWhiteTextFix) {
    console.log('✅ GOOD: All required elements are present on the live site');
    console.log('✅ GOOD: Theme system is active');
    console.log('✅ GOOD: Technical cards are present');
    console.log('✅ GOOD: White text fix has been applied');
    console.log('\n🎯 CONCLUSION: The contrast fix should be working correctly!');
    console.log('   Users should be able to read all text clearly in all themes.');
  } else {
    console.log('⚠️  ISSUES DETECTED:');
    if (!hasThemeScript) console.log('   - Theme system not found');
    if (!hasCards) console.log('   - Technical cards not found');
    if (!hasWhiteTextFix) console.log('   - White text fix not applied');
  }
  
  console.log('\n📁 Test Files Created:');
  console.log('   - theme-test.html: Local HTML file for manual testing');
  console.log('   - manual-theme-test.js: Contrast ratio analysis');
  console.log('   - live-site-test.js: Live site validation (this script)');
  
  console.log('\n🔗 Next Steps:');
  console.log('   1. Open theme-test.html in your browser to visually test themes');
  console.log('   2. Visit https://dd.kronisto.net/about to test the live site');
  console.log('   3. Use the theme selector to switch between themes');
  console.log('   4. Verify that all card text is clearly readable');
  
} catch (error) {
  console.error('❌ Error fetching page:', error.message);
  console.log('\n🔧 Troubleshooting:');
  console.log('   - Check if the site is accessible');
  console.log('   - Verify network connectivity');
  console.log('   - Try accessing https://dd.kronisto.net/about manually');
}

console.log('\n=== Test Complete ===');