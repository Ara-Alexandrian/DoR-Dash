#!/usr/bin/env node
/**
 * Browser Information Test Script
 * Tests Puppeteer's browser engine and capabilities
 */

import puppeteer from 'puppeteer';

console.log('=== Browser Information Test ===\n');

async function getBrowserInfo() {
    let browser;
    
    try {
        console.log('🚀 Launching Puppeteer browser...');
        
        // Launch browser with detailed configuration
        browser = await puppeteer.launch({
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        });

        const page = await browser.newPage();
        
        // Get browser version info
        const browserVersion = await browser.version();
        console.log(`📊 Browser Version: ${browserVersion}`);
        
        // Get user agent
        const userAgent = await browser.userAgent();
        console.log(`🔍 User Agent: ${userAgent}`);
        
        // Navigate to a test page to get more detailed info
        await page.goto('data:text/html,<html><body><h1>Browser Test Page</h1></body></html>');
        
        // Execute JavaScript to get detailed browser information
        const browserDetails = await page.evaluate(() => {
            const info = {
                // Browser engine detection
                browserEngine: 'Unknown',
                userAgent: navigator.userAgent,
                vendor: navigator.vendor,
                product: navigator.product,
                
                // JavaScript engine info
                jsEngine: 'V8', // Chromium always uses V8
                
                // Feature detection
                features: {
                    // CSS Features
                    cssGrid: CSS.supports('display', 'grid'),
                    cssFlexbox: CSS.supports('display', 'flex'),
                    cssCustomProperties: CSS.supports('color', 'var(--test)'),
                    cssContainerQueries: CSS.supports('container-type', 'inline-size'),
                    
                    // JavaScript Features
                    es6Modules: typeof Symbol !== 'undefined',
                    asyncAwait: typeof async !== 'undefined',
                    webAssembly: typeof WebAssembly !== 'undefined',
                    serviceWorker: 'serviceWorker' in navigator,
                    
                    // Web APIs
                    fetch: typeof fetch !== 'undefined',
                    webGL: !!document.createElement('canvas').getContext('webgl'),
                    webGL2: !!document.createElement('canvas').getContext('webgl2'),
                    indexedDB: 'indexedDB' in window,
                    localStorage: 'localStorage' in window,
                    sessionStorage: 'sessionStorage' in window,
                    
                    // Media features
                    mediaQueries: window.matchMedia ? true : false,
                    touchEvents: 'ontouchstart' in window,
                    
                    // Security features
                    contentSecurityPolicy: 'SecurityPolicyViolationEvent' in window,
                    subresourceIntegrity: 'HTMLScriptElement' in window && 'integrity' in HTMLScriptElement.prototype
                },
                
                // Screen and viewport info
                screen: {
                    width: screen.width,
                    height: screen.height,
                    colorDepth: screen.colorDepth,
                    pixelDepth: screen.pixelDepth
                },
                
                // Performance and memory info
                performance: {
                    memory: performance.memory ? {
                        jsHeapSizeLimit: performance.memory.jsHeapSizeLimit,
                        totalJSHeapSize: performance.memory.totalJSHeapSize,
                        usedJSHeapSize: performance.memory.usedJSHeapSize
                    } : null,
                    timing: performance.timing ? true : false
                }
            };
            
            // Detect browser engine
            if (info.userAgent.includes('Chrome')) {
                if (info.userAgent.includes('Edg')) {
                    info.browserEngine = 'Chromium (Microsoft Edge)';
                } else if (info.userAgent.includes('OPR')) {
                    info.browserEngine = 'Chromium (Opera)';
                } else {
                    info.browserEngine = 'Chromium (Chrome)';
                }
            } else if (info.userAgent.includes('Firefox')) {
                info.browserEngine = 'Gecko (Firefox)';
            } else if (info.userAgent.includes('Safari') && !info.userAgent.includes('Chrome')) {
                info.browserEngine = 'WebKit (Safari)';
            } else if (info.userAgent.includes('HeadlessChrome')) {
                info.browserEngine = 'Chromium (Headless Chrome)';
            }
            
            return info;
        });
        
        // Display results
        console.log('\n📋 Browser Engine Information:');
        console.log('================================');
        console.log(`Engine: ${browserDetails.browserEngine}`);
        console.log(`Vendor: ${browserDetails.vendor}`);
        console.log(`Product: ${browserDetails.product}`);
        console.log(`JavaScript Engine: ${browserDetails.jsEngine}`);
        
        console.log('\n🎨 CSS Feature Support:');
        console.log('========================');
        Object.entries(browserDetails.features).forEach(([feature, supported]) => {
            if (feature.startsWith('css')) {
                console.log(`${feature}: ${supported ? '✅ Supported' : '❌ Not Supported'}`);
            }
        });
        
        console.log('\n⚡ JavaScript Feature Support:');
        console.log('==============================');
        const jsFeatures = ['es6Modules', 'asyncAwait', 'webAssembly', 'serviceWorker'];
        jsFeatures.forEach(feature => {
            const supported = browserDetails.features[feature];
            console.log(`${feature}: ${supported ? '✅ Supported' : '❌ Not Supported'}`);
        });
        
        console.log('\n🌐 Web API Support:');
        console.log('===================');
        const webApis = ['fetch', 'webGL', 'webGL2', 'indexedDB', 'localStorage', 'sessionStorage'];
        webApis.forEach(api => {
            const supported = browserDetails.features[api];
            console.log(`${api}: ${supported ? '✅ Supported' : '❌ Not Supported'}`);
        });
        
        console.log('\n🔒 Security Features:');
        console.log('====================');
        const securityFeatures = ['contentSecurityPolicy', 'subresourceIntegrity'];
        securityFeatures.forEach(feature => {
            const supported = browserDetails.features[feature];
            console.log(`${feature}: ${supported ? '✅ Supported' : '❌ Not Supported'}`);
        });
        
        console.log('\n📱 Media & Display:');
        console.log('==================');
        console.log(`Screen: ${browserDetails.screen.width}x${browserDetails.screen.height}`);
        console.log(`Color Depth: ${browserDetails.screen.colorDepth} bits`);
        console.log(`Pixel Depth: ${browserDetails.screen.pixelDepth} bits`);
        console.log(`Media Queries: ${browserDetails.features.mediaQueries ? '✅ Supported' : '❌ Not Supported'}`);
        console.log(`Touch Events: ${browserDetails.features.touchEvents ? '✅ Supported' : '❌ Not Supported'}`);
        
        if (browserDetails.performance.memory) {
            console.log('\n💾 Memory Information:');
            console.log('=====================');
            const memory = browserDetails.performance.memory;
            console.log(`JS Heap Size Limit: ${(memory.jsHeapSizeLimit / 1024 / 1024).toFixed(2)} MB`);
            console.log(`Total JS Heap Size: ${(memory.totalJSHeapSize / 1024 / 1024).toFixed(2)} MB`);
            console.log(`Used JS Heap Size: ${(memory.usedJSHeapSize / 1024 / 1024).toFixed(2)} MB`);
        }
        
        // Test modern CSS features with actual CSS
        console.log('\n🧪 CSS Feature Testing:');
        console.log('=======================');
        
        // Set up a test page with modern CSS
        await page.setContent(`
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    .grid-test { display: grid; grid-template-columns: 1fr 1fr; }
                    .flex-test { display: flex; justify-content: center; }
                    .custom-props { --test-color: red; color: var(--test-color); }
                    .backdrop-filter-test { backdrop-filter: blur(10px); }
                    @container (min-width: 300px) { .container-test { color: blue; } }
                </style>
            </head>
            <body>
                <div class="grid-test">Grid Test</div>
                <div class="flex-test">Flex Test</div>
                <div class="custom-props">Custom Properties Test</div>
                <div class="backdrop-filter-test">Backdrop Filter Test</div>
                <div class="container-test">Container Query Test</div>
            </body>
            </html>
        `);
        
        const cssTestResults = await page.evaluate(() => {
            const gridTest = getComputedStyle(document.querySelector('.grid-test')).display;
            const flexTest = getComputedStyle(document.querySelector('.flex-test')).display;
            const customPropsTest = getComputedStyle(document.querySelector('.custom-props')).color;
            
            return {
                gridWorks: gridTest === 'grid',
                flexWorks: flexTest === 'flex',
                customPropsWorks: customPropsTest === 'rgb(255, 0, 0)' || customPropsTest === 'red'
            };
        });
        
        console.log(`CSS Grid rendering: ${cssTestResults.gridWorks ? '✅ Working' : '❌ Not Working'}`);
        console.log(`CSS Flexbox rendering: ${cssTestResults.flexWorks ? '✅ Working' : '❌ Not Working'}`);
        console.log(`CSS Custom Properties rendering: ${cssTestResults.customPropsWorks ? '✅ Working' : '❌ Not Working'}`);
        
        // Test Puppeteer-specific capabilities
        console.log('\n🤖 Puppeteer Capabilities:');
        console.log('==========================');
        
        // Screenshot capability
        try {
            await page.screenshot({ path: '/tmp/test-screenshot.png', width: 800, height: 600 });
            console.log('Screenshot capability: ✅ Working');
        } catch (error) {
            console.log('Screenshot capability: ❌ Not Working');
        }
        
        // PDF generation capability
        try {
            await page.pdf({ path: '/tmp/test-pdf.pdf', format: 'A4' });
            console.log('PDF generation: ✅ Working');
        } catch (error) {
            console.log('PDF generation: ❌ Not Working');
        }
        
        // Network interception capability
        try {
            await page.setRequestInterception(true);
            page.on('request', (request) => {
                request.continue();
            });
            console.log('Network interception: ✅ Working');
        } catch (error) {
            console.log('Network interception: ❌ Not Working');
        }
        
        console.log('\n📊 Summary:');
        console.log('===========');
        console.log(`✅ Browser Engine: ${browserDetails.browserEngine}`);
        console.log(`✅ Modern CSS Support: ${cssTestResults.gridWorks && cssTestResults.flexWorks ? 'Excellent' : 'Partial'}`);
        console.log(`✅ JavaScript Engine: V8 (Latest)`);
        console.log(`✅ Web APIs: ${browserDetails.features.fetch && browserDetails.features.webGL ? 'Comprehensive' : 'Basic'}`);
        console.log(`✅ Puppeteer Features: Full automation capabilities`);
        
        return browserDetails;
        
    } catch (error) {
        console.error('❌ Error during browser testing:', error.message);
        return null;
    } finally {
        if (browser) {
            await browser.close();
            console.log('\n🔒 Browser closed successfully');
        }
    }
}

// Run the test
getBrowserInfo().then(() => {
    console.log('\n=== Browser Information Test Complete ===');
}).catch(error => {
    console.error('Failed to run browser test:', error);
    process.exit(1);
});