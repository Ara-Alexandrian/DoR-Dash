#!/usr/bin/env node

/**
 * Comprehensive test script for DoR-Dash Presentation Assignment functionality
 * Tests the presentation assignment page with different themes and user interactions
 */

import puppeteer from 'puppeteer';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const BASE_URL = 'https://dd.kronisto.net';
const CREDENTIALS = {
    username: 'cerebro',
    password: '123'
};

const THEMES = ['light', 'dark', 'dracula', 'mbp', 'lsu'];
const SCREENSHOT_DIR = path.join(__dirname, 'test-screenshots');

class PresentationAssignmentTester {
    constructor() {
        this.browser = null;
        this.page = null;
        this.results = {
            loginSuccess: false,
            navigationSuccess: false,
            formTests: {},
            themeTests: {},
            functionalityTests: {},
            screenshots: [],
            errors: [],
            warnings: []
        };
    }

    async init() {
        console.log('🚀 Initializing Puppeteer browser...');
        
        this.browser = await puppeteer.launch({
            headless: false, // Set to true for production
            slowMo: 100,     // Slow down for better debugging
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        });

        this.page = await this.browser.newPage();
        await this.page.setViewport({ width: 1366, height: 768 });
        
        // Create screenshot directory
        try {
            await fs.mkdir(SCREENSHOT_DIR, { recursive: true });
        } catch (error) {
            console.warn('⚠️  Could not create screenshot directory:', error.message);
        }

        console.log('✅ Browser initialized successfully');
    }

    async login() {
        console.log('🔐 Attempting to login...');
        
        try {
            await this.page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle2' });
            
            // Fill login form
            await this.page.waitForSelector('input[name="username"], input[type="text"]', { timeout: 10000 });
            await this.page.type('input[name="username"], input[type="text"]', CREDENTIALS.username);
            await this.page.type('input[name="password"], input[type="password"]', CREDENTIALS.password);
            
            // Submit form
            await this.page.click('button[type="submit"], input[type="submit"]');
            
            // Wait for redirect or success indicator
            await this.page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 });
            
            // Check if we're on dashboard or logged in successfully
            const currentUrl = this.page.url();
            if (currentUrl.includes('/login')) {
                throw new Error('Login failed - still on login page');
            }
            
            this.results.loginSuccess = true;
            console.log('✅ Login successful');
            
            await this.takeScreenshot('01-login-success');
            
        } catch (error) {
            this.results.errors.push(`Login failed: ${error.message}`);
            console.error('❌ Login failed:', error.message);
            await this.takeScreenshot('01-login-failed');
            throw error;
        }
    }

    async navigateToAssignments() {
        console.log('🧭 Navigating to Presentation Assignments...');
        
        try {
            // Try multiple navigation methods
            const navigationMethods = [
                // Method 1: Direct URL
                async () => {
                    await this.page.goto(`${BASE_URL}/presentation-assignments`, { 
                        waitUntil: 'networkidle2',
                        timeout: 15000 
                    });
                },
                // Method 2: Through menu navigation
                async () => {
                    await this.page.waitForSelector('nav a, .nav-link', { timeout: 5000 });
                    const assignmentLink = await this.page.$x("//a[contains(text(), 'Presentation') or contains(text(), 'Assignment')]");
                    if (assignmentLink.length > 0) {
                        await assignmentLink[0].click();
                        await this.page.waitForNavigation({ waitUntil: 'networkidle2' });
                    } else {
                        throw new Error('Could not find presentation assignments link in navigation');
                    }
                }
            ];

            // Try each method
            let navSuccess = false;
            for (let i = 0; i < navigationMethods.length; i++) {
                try {
                    await navigationMethods[i]();
                    navSuccess = true;
                    break;
                } catch (error) {
                    console.warn(`⚠️  Navigation method ${i + 1} failed:`, error.message);
                    if (i === navigationMethods.length - 1) {
                        throw error;
                    }
                }
            }

            if (!navSuccess) {
                throw new Error('All navigation methods failed');
            }

            // Verify we're on the right page
            await this.page.waitForSelector('h1', { timeout: 10000 });
            const pageTitle = await this.page.$eval('h1', el => el.textContent);
            
            if (!pageTitle.toLowerCase().includes('presentation')) {
                this.results.warnings.push(`Page title "${pageTitle}" doesn't contain "presentation"`);
            }

            this.results.navigationSuccess = true;
            console.log('✅ Successfully navigated to Presentation Assignments');
            
            await this.takeScreenshot('02-navigation-success');
            
        } catch (error) {
            this.results.errors.push(`Navigation failed: ${error.message}`);
            console.error('❌ Navigation failed:', error.message);
            await this.takeScreenshot('02-navigation-failed');
            throw error;
        }
    }

    async testFormFunctionality() {
        console.log('📝 Testing form functionality...');
        
        try {
            // Check if "New Assignment" button exists (faculty/admin only)
            const newAssignmentBtn = await this.page.$('button:contains("New Assignment"), button[class*="create"], button[class*="new"]');
            
            if (!newAssignmentBtn) {
                this.results.formTests.createButtonVisible = false;
                this.results.warnings.push('New Assignment button not found - user may not have faculty/admin permissions');
                console.log('⚠️  New Assignment button not found - checking view-only mode');
                return await this.testViewOnlyMode();
            }

            this.results.formTests.createButtonVisible = true;
            
            // Click to open create form
            await newAssignmentBtn.click();
            await this.page.waitForTimeout(1000); // Wait for form animation
            
            await this.takeScreenshot('03-form-opened');

            // Test student dropdown
            console.log('  📋 Testing student dropdown...');
            await this.page.waitForSelector('select[id="student"], select:contains("Student")', { timeout: 5000 });
            const studentOptions = await this.page.$$eval('select[id="student"] option, select:contains("Student") option', 
                options => options.length);
            
            this.results.formTests.studentsLoaded = studentOptions > 1; // More than just placeholder
            console.log(`    ✅ Found ${studentOptions} student options`);

            // Test meeting dropdown
            console.log('  📅 Testing meeting dropdown...');
            const meetingSelect = await this.page.$('select[id="meeting"], select:contains("Meeting")');
            if (meetingSelect) {
                const meetingOptions = await this.page.$$eval('select[id="meeting"] option, select:contains("Meeting") option',
                    options => options.length);
                this.results.formTests.meetingsLoaded = meetingOptions > 1;
                console.log(`    ✅ Found ${meetingOptions} meeting options`);
            }

            // Test presentation types
            console.log('  🎭 Testing presentation types...');
            const typeSelect = await this.page.$('select[id="type"], select:contains("Type")');
            if (typeSelect) {
                const typeOptions = await this.page.$$eval('select[id="type"] option, select:contains("Type") option',
                    options => options.map(opt => opt.textContent));
                this.results.formTests.presentationTypes = typeOptions;
                console.log(`    ✅ Found presentation types: ${typeOptions.join(', ')}`);
            }

            // Test grillometer settings
            console.log('  🔥 Testing grillometer functionality...');
            await this.testGrillometer();

            // Test form submission (with dummy data)
            await this.testFormSubmission();

            console.log('✅ Form functionality tests completed');

        } catch (error) {
            this.results.errors.push(`Form testing failed: ${error.message}`);
            console.error('❌ Form testing failed:', error.message);
            await this.takeScreenshot('03-form-test-failed');
        }
    }

    async testGrillometer() {
        console.log('    🔥 Testing grillometer settings...');
        
        try {
            // Look for grillometer section
            const grillometerSection = await this.page.$('[class*="grillometer"], .grillometer, h3:contains("Grillometer")');
            
            if (!grillometerSection) {
                this.results.warnings.push('Grillometer section not found');
                return;
            }

            // Test each grillometer setting (novelty, methodology, delivery)
            const grillometerTypes = ['novelty', 'methodology', 'delivery'];
            
            for (const type of grillometerTypes) {
                const radioButtons = await this.page.$$(`input[type="radio"][name*="${type}"], input[type="radio"][bind:group*="${type}"]`);
                
                if (radioButtons.length >= 3) {
                    this.results.formTests[`grillometer_${type}`] = true;
                    
                    // Test clicking different levels
                    await radioButtons[1].click(); // Click moderate level
                    await this.page.waitForTimeout(200);
                    
                    console.log(`      ✅ ${type} grillometer working (${radioButtons.length} levels)`);
                } else {
                    this.results.formTests[`grillometer_${type}`] = false;
                    this.results.warnings.push(`${type} grillometer has insufficient options (${radioButtons.length})`);
                }
            }

            await this.takeScreenshot('04-grillometer-test');

        } catch (error) {
            this.results.warnings.push(`Grillometer testing failed: ${error.message}`);
            console.warn('⚠️  Grillometer testing failed:', error.message);
        }
    }

    async testFormSubmission() {
        console.log('    ✉️  Testing form submission flow...');
        
        try {
            // Fill required fields with test data
            await this.page.type('input[id="title"], input[placeholder*="title"]', 'Test Assignment');
            
            // Select first student if available
            const studentSelect = await this.page.$('select[id="student"]');
            if (studentSelect) {
                await this.page.select('select[id="student"]', '1'); // Try to select first student
            }

            await this.takeScreenshot('05-form-filled');

            // Try to submit (but cancel to avoid creating test data)
            const submitBtn = await this.page.$('button[type="submit"], button:contains("Create"), button:contains("Submit")');
            const cancelBtn = await this.page.$('button:contains("Cancel"), button[type="button"]');
            
            if (submitBtn && cancelBtn) {
                // Test that submit button is present and clickable
                this.results.formTests.submitButtonPresent = true;
                
                // Click cancel to close form
                await cancelBtn.click();
                await this.page.waitForTimeout(1000);
                
                this.results.formTests.cancelFunctionality = true;
                console.log('      ✅ Form submission flow tested (cancelled to avoid test data)');
            }

        } catch (error) {
            this.results.warnings.push(`Form submission test failed: ${error.message}`);
            console.warn('⚠️  Form submission test failed:', error.message);
        }
    }

    async testViewOnlyMode() {
        console.log('  👁️  Testing view-only mode...');
        
        try {
            // Check for existing assignments display
            const assignmentCards = await this.page.$$('.assignment, [class*="assignment"], .card, [class*="card"]');
            
            this.results.formTests.viewOnlyMode = true;
            this.results.formTests.existingAssignments = assignmentCards.length;
            
            if (assignmentCards.length > 0) {
                console.log(`    ✅ Found ${assignmentCards.length} existing assignments in view-only mode`);
                await this.takeScreenshot('03-assignments-view');
            } else {
                console.log('    ℹ️  No existing assignments found');
                await this.takeScreenshot('03-no-assignments');
            }

        } catch (error) {
            this.results.warnings.push(`View-only mode test failed: ${error.message}`);
        }
    }

    async testThemes() {
        console.log('🎨 Testing all themes...');
        
        for (const theme of THEMES) {
            console.log(`  🎭 Testing ${theme} theme...`);
            
            try {
                // Look for theme toggle/selector
                const themeToggle = await this.page.$('[data-theme], .theme-toggle, select[class*="theme"], button[class*="theme"]');
                
                if (themeToggle) {
                    // Try to select the theme
                    const tagName = await themeToggle.evaluate(el => el.tagName.toLowerCase());
                    
                    if (tagName === 'select') {
                        await this.page.select(themeToggle, theme);
                    } else {
                        // For buttons or other elements, try to find theme-specific selectors
                        const themeButton = await this.page.$(`[data-theme="${theme}"], button:contains("${theme}"), .theme-${theme}`);
                        if (themeButton) {
                            await themeButton.click();
                        }
                    }
                    
                    await this.page.waitForTimeout(1000); // Wait for theme change
                    
                    // Verify theme applied
                    const bodyClass = await this.page.$eval('html, body', el => el.className);
                    const documentClass = await this.page.evaluate(() => document.documentElement.className);
                    
                    this.results.themeTests[theme] = {
                        applied: bodyClass.includes(theme) || documentClass.includes(theme),
                        bodyClass,
                        documentClass
                    };
                    
                    await this.takeScreenshot(`06-theme-${theme}`);
                    
                    console.log(`    ✅ ${theme} theme tested`);
                    
                } else {
                    // Manually set theme via localStorage and reload
                    await this.page.evaluate((themeName) => {
                        localStorage.setItem('theme', themeName);
                        document.documentElement.classList.remove('light', 'dark', 'dracula', 'mbp', 'lsu');
                        document.documentElement.classList.add(themeName);
                    }, theme);
                    
                    await this.page.reload({ waitUntil: 'networkidle2' });
                    await this.page.waitForTimeout(1000);
                    
                    const documentClass = await this.page.evaluate(() => document.documentElement.className);
                    
                    this.results.themeTests[theme] = {
                        applied: documentClass.includes(theme),
                        method: 'localStorage',
                        documentClass
                    };
                    
                    await this.takeScreenshot(`06-theme-${theme}`);
                    console.log(`    ✅ ${theme} theme applied via localStorage`);
                }
                
            } catch (error) {
                this.results.themeTests[theme] = { error: error.message };
                this.results.warnings.push(`Theme ${theme} test failed: ${error.message}`);
                console.warn(`    ⚠️  Theme ${theme} test failed:`, error.message);
            }
        }
    }

    async testResponsiveness() {
        console.log('📱 Testing responsive design...');
        
        const viewports = [
            { name: 'Desktop', width: 1366, height: 768 },
            { name: 'Tablet', width: 768, height: 1024 },
            { name: 'Mobile', width: 375, height: 667 }
        ];

        for (const viewport of viewports) {
            try {
                await this.page.setViewport({ width: viewport.width, height: viewport.height });
                await this.page.waitForTimeout(1000);
                
                await this.takeScreenshot(`07-responsive-${viewport.name.toLowerCase()}`);
                
                // Check if elements are properly responsive
                const isResponsive = await this.page.evaluate(() => {
                    const body = document.body;
                    return {
                        hasOverflow: body.scrollWidth > body.clientWidth,
                        bodyWidth: body.clientWidth,
                        scrollWidth: body.scrollWidth
                    };
                });
                
                this.results.functionalityTests[`responsive_${viewport.name}`] = {
                    viewport,
                    isResponsive: !isResponsive.hasOverflow,
                    metrics: isResponsive
                };
                
                console.log(`  ✅ ${viewport.name} (${viewport.width}x${viewport.height}) tested`);
                
            } catch (error) {
                this.results.warnings.push(`Responsive test for ${viewport.name} failed: ${error.message}`);
            }
        }

        // Reset to desktop viewport
        await this.page.setViewport({ width: 1366, height: 768 });
    }

    async testAccessibility() {
        console.log('♿ Testing accessibility features...');
        
        try {
            // Check for proper heading structure
            const headings = await this.page.$$eval('h1, h2, h3, h4, h5, h6', 
                headings => headings.map(h => ({ tag: h.tagName, text: h.textContent.trim() })));
            
            this.results.functionalityTests.accessibility = {
                headingStructure: headings,
                hasH1: headings.some(h => h.tag === 'H1'),
                headingCount: headings.length
            };

            // Check for alt text on images
            const images = await this.page.$$eval('img', 
                imgs => imgs.map(img => ({ src: img.src, alt: img.alt, hasAlt: !!img.alt })));
            
            this.results.functionalityTests.accessibility.images = images;
            this.results.functionalityTests.accessibility.imagesWithoutAlt = images.filter(img => !img.hasAlt).length;

            // Check for proper form labels
            const formInputs = await this.page.$$eval('input, select, textarea', 
                inputs => inputs.map(input => ({
                    type: input.type || input.tagName,
                    id: input.id,
                    hasLabel: !!document.querySelector(`label[for="${input.id}"]`),
                    ariaLabel: input.getAttribute('aria-label'),
                    placeholder: input.placeholder
                })));
            
            this.results.functionalityTests.accessibility.formInputs = formInputs;

            console.log(`  ✅ Accessibility check completed - ${headings.length} headings, ${images.length} images`);

        } catch (error) {
            this.results.warnings.push(`Accessibility test failed: ${error.message}`);
        }
    }

    async takeScreenshot(name) {
        try {
            const filename = `${name}-${Date.now()}.png`;
            const filepath = path.join(SCREENSHOT_DIR, filename);
            
            await this.page.screenshot({ 
                path: filepath, 
                fullPage: true,
                type: 'png'
            });
            
            this.results.screenshots.push({
                name,
                filename,
                filepath,
                timestamp: new Date().toISOString()
            });
            
            console.log(`  📸 Screenshot saved: ${filename}`);
            
        } catch (error) {
            console.warn(`⚠️  Could not save screenshot ${name}:`, error.message);
        }
    }

    async runAllTests() {
        console.log('🧪 Starting comprehensive presentation assignment tests...\n');
        
        try {
            await this.init();
            await this.login();
            await this.navigateToAssignments();
            await this.testFormFunctionality();
            await this.testThemes();
            await this.testResponsiveness();
            await this.testAccessibility();
            
            console.log('\n✅ All tests completed successfully!');
            
        } catch (error) {
            console.error('\n❌ Test suite failed:', error.message);
            this.results.errors.push(`Test suite failed: ${error.message}`);
        }
    }

    async generateReport() {
        console.log('\n📊 Generating test report...');
        
        const report = {
            testSummary: {
                timestamp: new Date().toISOString(),
                url: BASE_URL,
                totalErrors: this.results.errors.length,
                totalWarnings: this.results.warnings.length,
                screenshotCount: this.results.screenshots.length
            },
            loginTest: {
                success: this.results.loginSuccess,
                status: this.results.loginSuccess ? '✅ PASS' : '❌ FAIL'
            },
            navigationTest: {
                success: this.results.navigationSuccess,
                status: this.results.navigationSuccess ? '✅ PASS' : '❌ FAIL'
            },
            formFunctionality: {
                ...this.results.formTests,
                status: Object.keys(this.results.formTests).length > 0 ? '✅ TESTED' : '⚠️  SKIPPED'
            },
            themeTests: {
                ...this.results.themeTests,
                testedThemes: Object.keys(this.results.themeTests),
                status: Object.keys(this.results.themeTests).length === THEMES.length ? '✅ ALL THEMES' : '⚠️  PARTIAL'
            },
            functionalityTests: {
                ...this.results.functionalityTests,
                status: Object.keys(this.results.functionalityTests).length > 0 ? '✅ TESTED' : '⚠️  SKIPPED'
            },
            errors: this.results.errors,
            warnings: this.results.warnings,
            screenshots: this.results.screenshots
        };

        // Save report to file
        const reportPath = path.join(__dirname, `presentation-assignment-test-report-${Date.now()}.json`);
        try {
            await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
            console.log(`📋 Detailed report saved: ${reportPath}`);
        } catch (error) {
            console.warn('⚠️  Could not save report file:', error.message);
        }

        // Print summary to console
        console.log('\n📊 TEST SUMMARY:');
        console.log('================');
        console.log(`🔐 Login: ${report.loginTest.status}`);
        console.log(`🧭 Navigation: ${report.navigationTest.status}`);
        console.log(`📝 Form Functionality: ${report.formFunctionality.status}`);
        console.log(`🎨 Theme Testing: ${report.themeTests.status}`);
        console.log(`🖥️  Functionality: ${report.functionalityTests.status}`);
        console.log(`📸 Screenshots: ${report.testSummary.screenshotCount} taken`);
        console.log(`⚠️  Warnings: ${report.testSummary.totalWarnings}`);
        console.log(`❌ Errors: ${report.testSummary.totalErrors}`);

        if (this.results.errors.length > 0) {
            console.log('\n❌ ERRORS:');
            this.results.errors.forEach((error, i) => console.log(`  ${i + 1}. ${error}`));
        }

        if (this.results.warnings.length > 0) {
            console.log('\n⚠️  WARNINGS:');
            this.results.warnings.forEach((warning, i) => console.log(`  ${i + 1}. ${warning}`));
        }

        console.log('\n🔍 DETAILED FINDINGS:');
        console.log('=====================');
        
        // Form functionality details
        if (Object.keys(this.results.formTests).length > 0) {
            console.log('\n📝 FORM FUNCTIONALITY:');
            Object.entries(this.results.formTests).forEach(([key, value]) => {
                const status = typeof value === 'boolean' ? (value ? '✅' : '❌') : '📊';
                console.log(`  ${status} ${key}: ${JSON.stringify(value)}`);
            });
        }

        // Theme details
        if (Object.keys(this.results.themeTests).length > 0) {
            console.log('\n🎨 THEME TESTING:');
            Object.entries(this.results.themeTests).forEach(([theme, result]) => {
                const status = result.applied ? '✅' : (result.error ? '❌' : '⚠️ ');
                console.log(`  ${status} ${theme}: ${result.applied ? 'Applied' : (result.error || 'Not applied')}`);
            });
        }

        // Grillometer specific findings
        const grillometerResults = Object.entries(this.results.formTests)
            .filter(([key]) => key.startsWith('grillometer_'));
        
        if (grillometerResults.length > 0) {
            console.log('\n🔥 GRILLOMETER SYSTEM:');
            grillometerResults.forEach(([key, value]) => {
                const aspect = key.replace('grillometer_', '').toUpperCase();
                const status = value ? '✅' : '❌';
                console.log(`  ${status} ${aspect}: ${value ? 'Working' : 'Issues detected'}`);
            });
        }

        return report;
    }

    async cleanup() {
        if (this.browser) {
            await this.browser.close();
            console.log('🧹 Browser closed');
        }
    }
}

// Main execution
async function main() {
    const tester = new PresentationAssignmentTester();
    
    try {
        await tester.runAllTests();
        await tester.generateReport();
        
    } catch (error) {
        console.error('💥 Fatal error:', error.message);
        process.exit(1);
        
    } finally {
        await tester.cleanup();
    }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch(console.error);
}

export default PresentationAssignmentTester;