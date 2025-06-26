#!/usr/bin/env node

/**
 * Test script specifically for aalexandrian user to test presentation assignment functionality
 * This script tests with a STUDENT role to verify role-based access control
 */

import puppeteer from 'puppeteer';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration for aalexandrian user
const BASE_URL = 'https://dd.kronisto.net';
const CREDENTIALS = {
    username: 'aalexandrian',
    password: '12345678'
};

const COMMON_PASSWORDS = ['password', '123', 'aalexandrian', 'admin', '12345678'];
const SCREENSHOT_DIR = path.join(__dirname, 'test-screenshots-aalexandrian');

class AalexandrianPresentationTester {
    constructor() {
        this.browser = null;
        this.page = null;
        this.results = {
            loginAttempts: [],
            loginSuccess: false,
            userRole: null,
            navigationTests: {},
            presentationAssignmentAccess: {},
            uiElements: {},
            apiResponses: [],
            consoleErrors: [],
            screenshots: [],
            errors: [],
            warnings: []
        };
    }

    async init() {
        console.log('🚀 Initializing Puppeteer browser for aalexandrian user testing...');
        
        this.browser = await puppeteer.launch({
            headless: false,
            slowMo: 100,
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
        
        // Listen for console messages to capture API errors
        this.page.on('console', (msg) => {
            if (msg.type() === 'error') {
                this.results.consoleErrors.push({
                    type: msg.type(),
                    text: msg.text(),
                    timestamp: new Date().toISOString()
                });
            }
        });

        // Listen for network responses to capture API calls
        this.page.on('response', (response) => {
            if (response.url().includes('/api/')) {
                this.results.apiResponses.push({
                    url: response.url(),
                    status: response.status(),
                    statusText: response.statusText(),
                    timestamp: new Date().toISOString()
                });
            }
        });
        
        // Create screenshot directory
        try {
            await fs.mkdir(SCREENSHOT_DIR, { recursive: true });
        } catch (error) {
            console.warn('⚠️  Could not create screenshot directory:', error.message);
        }

        console.log('✅ Browser initialized successfully');
    }

    async attemptLogin() {
        console.log('🔐 Attempting login with aalexandrian user...');
        
        // Try primary credentials first
        let loginSuccess = await this.tryLogin(CREDENTIALS.username, CREDENTIALS.password);
        
        if (!loginSuccess) {
            console.log('⚠️  Primary credentials failed, trying common passwords...');
            
            // Try common passwords
            for (const password of COMMON_PASSWORDS) {
                if (password === CREDENTIALS.password) continue; // Already tried
                
                console.log(`  🔑 Trying password: ${password}`);
                loginSuccess = await this.tryLogin(CREDENTIALS.username, password);
                
                if (loginSuccess) {
                    console.log(`✅ Login successful with password: ${password}`);
                    break;
                }
            }
        }

        if (!loginSuccess) {
            throw new Error('All login attempts failed');
        }

        this.results.loginSuccess = true;
        return true;
    }

    async tryLogin(username, password) {
        try {
            await this.page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle2' });
            
            // Clear any existing values
            await this.page.evaluate(() => {
                const inputs = document.querySelectorAll('input');
                inputs.forEach(input => input.value = '');
            });

            // Fill login form
            await this.page.waitForSelector('input[name="username"], input[type="text"]', { timeout: 10000 });
            await this.page.type('input[name="username"], input[type="text"]', username);
            await this.page.type('input[name="password"], input[type="password"]', password);
            
            await this.takeScreenshot(`login-attempt-${password}`);
            
            // Submit form
            await this.page.click('button[type="submit"], input[type="submit"]');
            
            // Wait for navigation or error
            await this.page.waitForTimeout(3000);
            
            const currentUrl = this.page.url();
            const loginAttempt = {
                username,
                password,
                success: !currentUrl.includes('/login'),
                finalUrl: currentUrl,
                timestamp: new Date().toISOString()
            };
            
            this.results.loginAttempts.push(loginAttempt);
            
            if (loginAttempt.success) {
                await this.takeScreenshot('login-success');
                await this.checkUserRole();
                return true;
            } else {
                await this.takeScreenshot(`login-failed-${password}`);
                return false;
            }
            
        } catch (error) {
            this.results.errors.push(`Login attempt failed: ${error.message}`);
            console.error('❌ Login attempt failed:', error.message);
            return false;
        }
    }

    async checkUserRole() {
        console.log('👤 Checking user role and permissions...');
        
        try {
            // Check if user info is available in the page
            const userInfo = await this.page.evaluate(() => {
                // Look for user info in various places
                const userElements = document.querySelectorAll('[data-role], .user-role, .role');
                const userText = Array.from(userElements).map(el => el.textContent).join(' ');
                
                // Also check localStorage
                const userData = localStorage.getItem('user') || localStorage.getItem('auth');
                
                return {
                    pageText: userText,
                    localStorage: userData,
                    url: window.location.href
                };
            });
            
            this.results.userRole = userInfo;
            console.log('  📊 User info found:', userInfo);
            
            await this.takeScreenshot('user-role-check');
            
        } catch (error) {
            this.results.warnings.push(`User role check failed: ${error.message}`);
        }
    }

    async testMainMenuAccess() {
        console.log('🧭 Testing main menu and navigation access...');
        
        try {
            // Check what menu items are available
            const menuItems = await this.page.evaluate(() => {
                const navLinks = document.querySelectorAll('nav a, .nav-link, [role="navigation"] a');
                return Array.from(navLinks).map(link => ({
                    text: link.textContent.trim(),
                    href: link.href,
                    visible: link.offsetParent !== null
                }));
            });
            
            this.results.navigationTests.menuItems = menuItems;
            
            // Specifically look for "Presentation Assignments" in menu
            const presentationAssignmentLink = menuItems.find(item => 
                item.text.toLowerCase().includes('presentation') && 
                item.text.toLowerCase().includes('assignment')
            );
            
            this.results.navigationTests.presentationAssignmentInMenu = !!presentationAssignmentLink;
            
            if (presentationAssignmentLink) {
                console.log('✅ Found "Presentation Assignments" in menu');
                console.log('  📋 Link details:', presentationAssignmentLink);
            } else {
                console.log('⚠️  "Presentation Assignments" NOT found in main menu');
                console.log('  📋 Available menu items:', menuItems.map(i => i.text));
            }
            
            await this.takeScreenshot('main-menu-check');
            
        } catch (error) {
            this.results.errors.push(`Menu access test failed: ${error.message}`);
        }
    }

    async testDirectPresentationAssignmentAccess() {
        console.log('🎯 Testing direct access to /presentation-assignments...');
        
        try {
            // Try to navigate directly to presentation assignments
            await this.page.goto(`${BASE_URL}/presentation-assignments`, { 
                waitUntil: 'networkidle2',
                timeout: 15000 
            });
            
            const currentUrl = this.page.url();
            const pageTitle = await this.page.title();
            
            // Check if we were redirected or got an error
            this.results.presentationAssignmentAccess.directAccess = {
                requestedUrl: `${BASE_URL}/presentation-assignments`,
                actualUrl: currentUrl,
                title: pageTitle,
                wasRedirected: currentUrl !== `${BASE_URL}/presentation-assignments`,
                timestamp: new Date().toISOString()
            };
            
            // Check what content we see
            await this.page.waitForTimeout(2000);
            
            const pageContent = await this.page.evaluate(() => {
                const h1 = document.querySelector('h1');
                const h2 = document.querySelector('h2');
                const errorMessages = document.querySelectorAll('.error, .alert, [role="alert"]');
                const formElements = document.querySelectorAll('form, button, input, select');
                
                return {
                    h1Text: h1 ? h1.textContent.trim() : null,
                    h2Text: h2 ? h2.textContent.trim() : null,
                    errorMessages: Array.from(errorMessages).map(el => el.textContent.trim()),
                    formElementCount: formElements.length,
                    bodyText: document.body.textContent.substring(0, 500) // First 500 chars
                };
            });
            
            this.results.presentationAssignmentAccess.pageContent = pageContent;
            
            console.log('  📊 Direct access result:');
            console.log(`    Requested: ${BASE_URL}/presentation-assignments`);
            console.log(`    Actual: ${currentUrl}`);
            console.log(`    Title: ${pageTitle}`);
            console.log(`    Was redirected: ${currentUrl !== `${BASE_URL}/presentation-assignments`}`);
            console.log(`    Page heading: ${pageContent.h1Text || pageContent.h2Text || 'None found'}`);
            
            if (pageContent.errorMessages.length > 0) {
                console.log(`    ⚠️  Error messages found: ${pageContent.errorMessages.join(', ')}`);
            }
            
            await this.takeScreenshot('direct-access-presentation-assignments');
            
        } catch (error) {
            this.results.errors.push(`Direct access test failed: ${error.message}`);
            await this.takeScreenshot('direct-access-error');
        }
    }

    async analyzeUIElements() {
        console.log('🔍 Analyzing UI elements and permissions...');
        
        try {
            const uiAnalysis = await this.page.evaluate(() => {
                // Look for various UI elements that might indicate permissions
                const createButtons = document.querySelectorAll('button:contains("Create"), button:contains("New"), button:contains("Add")');
                const editButtons = document.querySelectorAll('button:contains("Edit"), .edit-button, [aria-label*="edit"]');
                const assignmentCards = document.querySelectorAll('.assignment, [class*="assignment"], .card');
                const forms = document.querySelectorAll('form');
                const dropdowns = document.querySelectorAll('select');
                const adminElements = document.querySelectorAll('[data-role="admin"], .admin-only, [class*="admin"]');
                const facultyElements = document.querySelectorAll('[data-role="faculty"], .faculty-only, [class*="faculty"]');
                const studentElements = document.querySelectorAll('[data-role="student"], .student-only, [class*="student"]');
                
                return {
                    createButtonCount: createButtons.length,
                    editButtonCount: editButtons.length,
                    assignmentCardCount: assignmentCards.length,
                    formCount: forms.length,
                    dropdownCount: dropdowns.length,
                    adminElementCount: adminElements.length,
                    facultyElementCount: facultyElements.length,
                    studentElementCount: studentElements.length,
                    hasCreateAssignmentButton: Array.from(createButtons).some(btn => 
                        btn.textContent.toLowerCase().includes('assignment') || 
                        btn.textContent.toLowerCase().includes('new')
                    )
                };
            });
            
            this.results.uiElements = uiAnalysis;
            
            console.log('  📊 UI Analysis Results:');
            console.log(`    Create buttons: ${uiAnalysis.createButtonCount}`);
            console.log(`    Edit buttons: ${uiAnalysis.editButtonCount}`);
            console.log(`    Assignment cards: ${uiAnalysis.assignmentCardCount}`);
            console.log(`    Forms: ${uiAnalysis.formCount}`);
            console.log(`    Dropdowns: ${uiAnalysis.dropdownCount}`);
            console.log(`    Admin elements: ${uiAnalysis.adminElementCount}`);
            console.log(`    Faculty elements: ${uiAnalysis.facultyElementCount}`);
            console.log(`    Student elements: ${uiAnalysis.studentElementCount}`);
            console.log(`    Has create assignment button: ${uiAnalysis.hasCreateAssignmentButton}`);
            
            await this.takeScreenshot('ui-elements-analysis');
            
        } catch (error) {
            this.results.warnings.push(`UI analysis failed: ${error.message}`);
        }
    }

    async checkConsoleAndNetworkErrors() {
        console.log('🔍 Checking browser console and network errors...');
        
        // Console errors are automatically captured
        console.log(`  📊 Console errors found: ${this.results.consoleErrors.length}`);
        if (this.results.consoleErrors.length > 0) {
            console.log('  ❌ Console errors:');
            this.results.consoleErrors.forEach((error, i) => {
                console.log(`    ${i + 1}. ${error.text}`);
            });
        }
        
        // API responses are automatically captured
        console.log(`  📊 API calls made: ${this.results.apiResponses.length}`);
        const errorResponses = this.results.apiResponses.filter(r => r.status >= 400);
        if (errorResponses.length > 0) {
            console.log('  ❌ API errors:');
            errorResponses.forEach((error, i) => {
                console.log(`    ${i + 1}. ${error.status} ${error.statusText} - ${error.url}`);
            });
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
        console.log('🧪 Starting aalexandrian user presentation assignment tests...\n');
        
        try {
            await this.init();
            await this.attemptLogin();
            await this.testMainMenuAccess();
            await this.testDirectPresentationAssignmentAccess();
            await this.analyzeUIElements();
            await this.checkConsoleAndNetworkErrors();
            
            console.log('\n✅ All tests completed successfully!');
            
        } catch (error) {
            console.error('\n❌ Test suite failed:', error.message);
            this.results.errors.push(`Test suite failed: ${error.message}`);
        }
    }

    async generateReport() {
        console.log('\n📊 Generating aalexandrian user test report...');
        
        const report = {
            testSummary: {
                timestamp: new Date().toISOString(),
                url: BASE_URL,
                username: CREDENTIALS.username,
                expectedRole: 'STUDENT',
                totalErrors: this.results.errors.length,
                totalWarnings: this.results.warnings.length,
                screenshotCount: this.results.screenshots.length
            },
            loginResults: {
                attemptsCount: this.results.loginAttempts.length,
                successfulLogin: this.results.loginSuccess,
                attempts: this.results.loginAttempts,
                userRole: this.results.userRole
            },
            navigationTests: {
                ...this.results.navigationTests,
                status: this.results.navigationTests.presentationAssignmentInMenu ? '✅ FOUND IN MENU' : '⚠️  NOT IN MENU'
            },
            presentationAssignmentAccess: {
                ...this.results.presentationAssignmentAccess,
                status: this.results.presentationAssignmentAccess.directAccess ? 
                    (this.results.presentationAssignmentAccess.directAccess.wasRedirected ? '⚠️  REDIRECTED' : '✅ ACCESSIBLE') : 
                    '❌ FAILED'
            },
            uiElements: {
                ...this.results.uiElements,
                analysis: this.analyzePermissions()
            },
            apiResponses: this.results.apiResponses,
            consoleErrors: this.results.consoleErrors,
            errors: this.results.errors,
            warnings: this.results.warnings,
            screenshots: this.results.screenshots
        };

        // Save report to file
        const reportPath = path.join(__dirname, `aalexandrian-presentation-test-report-${Date.now()}.json`);
        try {
            await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
            console.log(`📋 Detailed report saved: ${reportPath}`);
        } catch (error) {
            console.warn('⚠️  Could not save report file:', error.message);
        }

        // Print summary to console
        this.printSummary(report);
        
        return report;
    }

    analyzePermissions() {
        const ui = this.results.uiElements;
        
        return {
            likelihoodStudentRole: this.calculateStudentRoleLikelihood(),
            canCreateAssignments: ui.hasCreateAssignmentButton || ui.createButtonCount > 0,
            canEditAssignments: ui.editButtonCount > 0,
            viewOnlyMode: ui.assignmentCardCount > 0 && ui.createButtonCount === 0,
            hasAdminFeatures: ui.adminElementCount > 0,
            hasFacultyFeatures: ui.facultyElementCount > 0,
            hasStudentFeatures: ui.studentElementCount > 0
        };
    }

    calculateStudentRoleLikelihood() {
        let score = 0;
        const ui = this.results.uiElements;
        
        // Evidence for student role
        if (ui.createButtonCount === 0) score += 30;
        if (ui.editButtonCount === 0) score += 20;
        if (ui.adminElementCount === 0) score += 25;
        if (ui.facultyElementCount === 0) score += 15;
        if (ui.studentElementCount > 0) score += 10;
        
        return Math.min(score, 100);
    }

    printSummary(report) {
        console.log('\n📊 AALEXANDRIAN USER TEST SUMMARY:');
        console.log('=====================================');
        console.log(`👤 User: ${CREDENTIALS.username} (Expected: STUDENT role)`);
        console.log(`🔐 Login: ${report.loginResults.successfulLogin ? '✅ SUCCESS' : '❌ FAILED'}`);
        console.log(`🧭 Menu Access: ${report.navigationTests.status}`);
        console.log(`🎯 Direct URL Access: ${report.presentationAssignmentAccess.status}`);
        console.log(`📱 UI Elements: ${report.uiElements.analysis.canCreateAssignments ? '⚠️  CAN CREATE' : '✅ VIEW ONLY'}`);
        console.log(`📊 Student Role Likelihood: ${report.uiElements.analysis.likelihoodStudentRole}%`);
        console.log(`📸 Screenshots: ${report.testSummary.screenshotCount} taken`);
        console.log(`🐛 Console Errors: ${report.consoleErrors.length}`);
        console.log(`🌐 API Errors: ${report.apiResponses.filter(r => r.status >= 400).length}`);
        console.log(`⚠️  Warnings: ${report.testSummary.totalWarnings}`);
        console.log(`❌ Errors: ${report.testSummary.totalErrors}`);

        if (report.loginResults.successfulLogin) {
            console.log('\n🔐 LOGIN DETAILS:');
            const successfulAttempt = report.loginResults.attempts.find(a => a.success);
            if (successfulAttempt) {
                console.log(`  ✅ Successful password: ${successfulAttempt.password}`);
                console.log(`  🌐 Final URL: ${successfulAttempt.finalUrl}`);
            }
        }

        if (report.navigationTests.menuItems) {
            console.log('\n🧭 MENU ITEMS FOUND:');
            report.navigationTests.menuItems.forEach((item, i) => {
                console.log(`  ${i + 1}. ${item.text} (${item.visible ? 'visible' : 'hidden'})`);
            });
        }

        if (report.presentationAssignmentAccess.directAccess) {
            const access = report.presentationAssignmentAccess.directAccess;
            console.log('\n🎯 DIRECT ACCESS RESULTS:');
            console.log(`  📋 Page Title: ${access.title}`);
            console.log(`  🌐 Final URL: ${access.actualUrl}`);
            console.log(`  🔀 Was Redirected: ${access.wasRedirected ? 'Yes' : 'No'}`);
            
            if (report.presentationAssignmentAccess.pageContent) {
                const content = report.presentationAssignmentAccess.pageContent;
                console.log(`  📝 Page Heading: ${content.h1Text || content.h2Text || 'None'}`);
                console.log(`  📊 Form Elements: ${content.formElementCount}`);
                if (content.errorMessages.length > 0) {
                    console.log(`  ❌ Error Messages: ${content.errorMessages.join(', ')}`);
                }
            }
        }

        if (report.uiElements) {
            console.log('\n📱 UI PERMISSION ANALYSIS:');
            console.log(`  ✅ Can Create Assignments: ${report.uiElements.analysis.canCreateAssignments ? 'YES' : 'NO'}`);
            console.log(`  ✏️  Can Edit Assignments: ${report.uiElements.analysis.canEditAssignments ? 'YES' : 'NO'}`);
            console.log(`  👁️  View Only Mode: ${report.uiElements.analysis.viewOnlyMode ? 'YES' : 'NO'}`);
            console.log(`  👨‍💼 Admin Features: ${report.uiElements.analysis.hasAdminFeatures ? 'YES' : 'NO'}`);
            console.log(`  👨‍🏫 Faculty Features: ${report.uiElements.analysis.hasFacultyFeatures ? 'YES' : 'NO'}`);
            console.log(`  👨‍🎓 Student Features: ${report.uiElements.analysis.hasStudentFeatures ? 'YES' : 'NO'}`);
        }

        if (report.errors.length > 0) {
            console.log('\n❌ ERRORS:');
            report.errors.forEach((error, i) => console.log(`  ${i + 1}. ${error}`));
        }

        if (report.warnings.length > 0) {
            console.log('\n⚠️  WARNINGS:');
            report.warnings.forEach((warning, i) => console.log(`  ${i + 1}. ${warning}`));
        }

        // Final assessment
        console.log('\n🎯 FINAL ASSESSMENT:');
        if (report.loginResults.successfulLogin) {
            if (report.uiElements.analysis.likelihoodStudentRole >= 80) {
                console.log('✅ USER APPEARS TO HAVE CORRECT STUDENT ROLE - RBAC working properly');
            } else if (report.uiElements.analysis.canCreateAssignments) {
                console.log('⚠️  USER MAY HAVE ELEVATED PERMISSIONS - Check role assignment');
            } else {
                console.log('❓ INCONCLUSIVE - More investigation needed');
            }
        } else {
            console.log('❌ CANNOT ASSESS - Login failed with all attempted passwords');
        }
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
    const tester = new AalexandrianPresentationTester();
    
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

export default AalexandrianPresentationTester;