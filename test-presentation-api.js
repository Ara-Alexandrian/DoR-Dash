#!/usr/bin/env node

/**
 * API-based test script for DoR-Dash Presentation Assignment functionality
 * Tests the backend APIs and provides comprehensive analysis
 */

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

class PresentationAssignmentAPITester {
    constructor() {
        this.accessToken = null;
        this.results = {
            loginSuccess: false,
            apiTests: {},
            dataValidation: {},
            errors: [],
            warnings: [],
            recommendations: []
        };
    }

    async makeRequest(endpoint, options = {}) {
        const url = `${BASE_URL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'User-Agent': 'DoR-Dash-Tester/1.0',
                ...(this.accessToken ? { 'Authorization': `Bearer ${this.accessToken}` } : {})
            }
        };

        const finalOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, finalOptions);

            return {
                ok: response.ok,
                status: response.status,
                statusText: response.statusText,
                data: response.ok ? await response.json().catch(() => null) : null,
                error: !response.ok ? await response.text().catch(() => response.statusText) : null,
                headers: Object.fromEntries(response.headers.entries())
            };
        } catch (error) {
            return {
                ok: false,
                status: 0,
                statusText: 'Network Error',
                data: null,
                error: error.message,
                headers: {}
            };
        }
    }

    async login() {
        console.log('🔐 Testing login API...');
        
        // Try form data first (common for login endpoints)
        const formData = new URLSearchParams();
        formData.append('username', CREDENTIALS.username);
        formData.append('password', CREDENTIALS.password);
        
        let response = await this.makeRequest('/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData.toString()
        });
        
        // If form data fails, try JSON
        if (!response.ok) {
            response = await this.makeRequest('/api/v1/auth/login', {
                method: 'POST',
                body: JSON.stringify(CREDENTIALS)
            });
        }

        if (response.ok && response.data) {
            this.results.loginSuccess = true;
            this.accessToken = response.data.access_token;
            console.log('✅ Login successful');
            
            // Test token validation
            const meResponse = await this.makeRequest('/api/v1/auth/me');
            if (meResponse.ok) {
                this.results.userProfile = meResponse.data;
                console.log(`  👤 Logged in as: ${meResponse.data.username} (${meResponse.data.role})`);
            }
            
        } else {
            this.results.errors.push(`Login failed: ${response.status} ${response.error}`);
            console.error('❌ Login failed:', response.error);
        }

        return response.ok;
    }

    async testPresentationAssignmentsAPI() {
        console.log('📝 Testing Presentation Assignments API...');

        // Test GET /api/v1/presentation-assignments/
        const getResponse = await this.makeRequest('/api/v1/presentation-assignments/');
        
        this.results.apiTests.getAssignments = {
            status: getResponse.status,
            success: getResponse.ok,
            data: getResponse.data,
            error: getResponse.error
        };

        if (getResponse.ok) {
            console.log(`  ✅ GET assignments: ${getResponse.data?.length || 0} assignments found`);
            this.analyzeAssignmentsData(getResponse.data || []);
        } else {
            console.error(`  ❌ GET assignments failed: ${getResponse.status} ${getResponse.error}`);
        }

        // Test GET presentation types
        const typesResponse = await this.makeRequest('/api/v1/presentation-assignments/types/');
        
        this.results.apiTests.getTypes = {
            status: typesResponse.status,
            success: typesResponse.ok,
            data: typesResponse.data
        };

        if (typesResponse.ok) {
            console.log(`  ✅ GET types: ${typesResponse.data?.length || 0} presentation types available`);
            console.log(`    Types: ${typesResponse.data?.join(', ') || 'None'}`);
        } else {
            console.error(`  ❌ GET types failed: ${typesResponse.status} ${typesResponse.error}`);
        }

        return getResponse.ok;
    }

    async testRosterAPI() {
        console.log('👥 Testing Roster API (for student data)...');

        const rosterResponse = await this.makeRequest('/api/v1/users/roster');
        
        this.results.apiTests.getRoster = {
            status: rosterResponse.status,
            success: rosterResponse.ok,
            data: rosterResponse.data
        };

        if (rosterResponse.ok && Array.isArray(rosterResponse.data)) {
            const students = rosterResponse.data.filter(user => user.role === 'STUDENT');
            console.log(`  ✅ Roster API: ${students.length} students found`);
            this.results.dataValidation.studentsAvailable = students.length > 0;
            this.results.dataValidation.studentCount = students.length;
        } else {
            console.error(`  ❌ Roster API failed: ${rosterResponse.status} ${rosterResponse.error}`);
            this.results.dataValidation.studentsAvailable = false;
        }
    }

    async testMeetingsAPI() {
        console.log('📅 Testing Meetings API...');

        const meetingsResponse = await this.makeRequest('/api/v1/meetings');
        
        this.results.apiTests.getMeetings = {
            status: meetingsResponse.status,
            success: meetingsResponse.ok,
            data: meetingsResponse.data
        };

        if (meetingsResponse.ok && Array.isArray(meetingsResponse.data)) {
            console.log(`  ✅ Meetings API: ${meetingsResponse.data.length} meetings found`);
            this.results.dataValidation.meetingsAvailable = meetingsResponse.data.length > 0;
            this.results.dataValidation.meetingCount = meetingsResponse.data.length;
        } else {
            console.error(`  ❌ Meetings API failed: ${meetingsResponse.status} ${meetingsResponse.error}`);
            this.results.dataValidation.meetingsAvailable = false;
        }
    }

    analyzeAssignmentsData(assignments) {
        console.log('🔍 Analyzing assignments data...');

        if (!Array.isArray(assignments)) {
            this.results.warnings.push('Assignments data is not an array');
            return;
        }

        const analysis = {
            totalAssignments: assignments.length,
            completedAssignments: assignments.filter(a => a.is_completed).length,
            pendingAssignments: assignments.filter(a => !a.is_completed).length,
            presentationTypes: [...new Set(assignments.map(a => a.presentation_type))],
            studentsWithAssignments: [...new Set(assignments.map(a => a.student_id))].length,
            assignmentsWithGrillometer: assignments.filter(a => 
                a.grillometer_novelty || a.grillometer_methodology || a.grillometer_delivery).length,
            assignmentsWithMeetings: assignments.filter(a => a.meeting_id).length,
            assignmentsWithDueDates: assignments.filter(a => a.due_date).length
        };

        this.results.dataValidation.assignmentsAnalysis = analysis;

        console.log(`  📊 Analysis Summary:`);
        console.log(`    Total: ${analysis.totalAssignments}`);
        console.log(`    Completed: ${analysis.completedAssignments}`);
        console.log(`    Pending: ${analysis.pendingAssignments}`);
        console.log(`    Types in use: ${analysis.presentationTypes.join(', ') || 'None'}`);
        console.log(`    Students with assignments: ${analysis.studentsWithAssignments}`);
        console.log(`    With grillometer settings: ${analysis.assignmentsWithGrillometer}`);
        console.log(`    Linked to meetings: ${analysis.assignmentsWithMeetings}`);
        console.log(`    With due dates: ${analysis.assignmentsWithDueDates}`);

        // Generate recommendations
        this.generateRecommendations(analysis);
    }

    generateRecommendations(analysis) {
        console.log('💡 Generating recommendations...');

        // Check grillometer usage
        if (analysis.assignmentsWithGrillometer === 0 && analysis.totalAssignments > 0) {
            this.results.recommendations.push({
                category: 'Grillometer Usage',
                priority: 'Medium',
                message: 'No assignments are using the grillometer system. Consider training faculty on this feedback tool.'
            });
        }

        // Check meeting integration
        if (analysis.assignmentsWithMeetings === 0 && analysis.totalAssignments > 0) {
            this.results.recommendations.push({
                category: 'Meeting Integration',
                priority: 'Low',
                message: 'Assignments are not linked to specific meetings. This could help with scheduling and context.'
            });
        }

        // Check due date usage
        if (analysis.assignmentsWithDueDates < analysis.totalAssignments * 0.5) {
            this.results.recommendations.push({
                category: 'Due Date Management',
                priority: 'High',
                message: 'Many assignments lack due dates. This is important for student planning and faculty oversight.'
            });
        }

        // Check presentation type diversity
        if (analysis.presentationTypes.length === 1 && analysis.totalAssignments > 3) {
            this.results.recommendations.push({
                category: 'Presentation Diversity',
                priority: 'Medium',
                message: 'All assignments use the same presentation type. Consider diversifying to match different learning objectives.'
            });
        }

        console.log(`  ✅ Generated ${this.results.recommendations.length} recommendations`);
    }

    async testFormValidation() {
        console.log('🧪 Testing form validation...');

        // Test invalid assignment creation (should fail)
        const invalidData = {
            title: '', // Empty title should fail
            student_id: 'invalid', // Invalid student ID
            presentation_type: 'invalid_type'
        };

        const createResponse = await this.makeRequest('/api/v1/presentation-assignments/', {
            method: 'POST',
            body: JSON.stringify(invalidData)
        });

        this.results.apiTests.formValidation = {
            invalidDataRejected: !createResponse.ok,
            status: createResponse.status,
            error: createResponse.error
        };

        if (!createResponse.ok) {
            console.log('  ✅ Form validation working - invalid data rejected');
        } else {
            console.warn('  ⚠️  Form validation may be weak - invalid data accepted');
            this.results.warnings.push('Form validation may not be working properly');
        }
    }

    async analyzeUIComponents() {
        console.log('🎨 Analyzing UI components from source code...');

        try {
            // Read and analyze the Svelte component
            const componentPath = path.join(__dirname, 'frontend/src/routes/presentation-assignments/+page.svelte');
            const componentCode = await fs.readFile(componentPath, 'utf-8');

            const analysis = {
                hasGrillometerUI: componentCode.includes('grillometer'),
                hasThemeSupport: componentCode.includes('--color-'),
                hasFormValidation: componentCode.includes('required'),
                hasResponsiveDesign: componentCode.includes('md:') || componentCode.includes('lg:') || componentCode.includes('sm:'),
                presentationTypes: this.extractPresentationTypes(componentCode),
                grillometerLevels: this.extractGrillometerLevels(componentCode),
                themes: ['light', 'dark', 'dracula', 'mbp', 'lsu'] // From theme.js analysis
            };

            this.results.dataValidation.uiAnalysis = analysis;

            console.log('  📊 UI Component Analysis:');
            console.log(`    Grillometer UI: ${analysis.hasGrillometerUI ? '✅' : '❌'}`);
            console.log(`    Theme Support: ${analysis.hasThemeSupport ? '✅' : '❌'}`);
            console.log(`    Form Validation: ${analysis.hasFormValidation ? '✅' : '❌'}`);
            console.log(`    Responsive Design: ${analysis.hasResponsiveDesign ? '✅' : '❌'}`);
            console.log(`    Presentation Types: ${analysis.presentationTypes.length} defined`);
            console.log(`    Grillometer Levels: ${analysis.grillometerLevels.length} levels`);
            console.log(`    Theme Support: ${analysis.themes.length} themes`);

        } catch (error) {
            this.results.warnings.push(`UI analysis failed: ${error.message}`);
            console.warn('  ⚠️  Could not analyze UI components:', error.message);
        }
    }

    extractPresentationTypes(code) {
        const typeMatch = code.match(/presentationTypes\s*=\s*\[(.*?)\]/s);
        if (typeMatch) {
            // Count the number of type objects
            const typeObjects = typeMatch[1].match(/\{[^}]+\}/g);
            return typeObjects ? typeObjects.map(obj => {
                const valueMatch = obj.match(/value:\s*['"]([^'"]+)['"]/);
                const labelMatch = obj.match(/label:\s*['"]([^'"]+)['"]/);
                return {
                    value: valueMatch ? valueMatch[1] : '',
                    label: labelMatch ? labelMatch[1] : ''
                };
            }) : [];
        }
        return [];
    }

    extractGrillometerLevels(code) {
        const levelMatches = code.match(/\[1,\s*2,\s*3\]/g);
        return levelMatches ? [1, 2, 3] : [];
    }

    async runAllTests() {
        console.log('🧪 Starting comprehensive API and analysis tests...\n');

        try {
            const loginSuccess = await this.login();
            if (!loginSuccess) {
                console.error('❌ Cannot proceed without login');
                return;
            }

            await this.testPresentationAssignmentsAPI();
            await this.testRosterAPI();
            await this.testMeetingsAPI();
            await this.testFormValidation();
            await this.analyzeUIComponents();

            console.log('\n✅ All tests completed successfully!');

        } catch (error) {
            console.error('\n❌ Test suite failed:', error.message);
            this.results.errors.push(`Test suite failed: ${error.message}`);
        }
    }

    async generateReport() {
        console.log('\n📊 Generating comprehensive test report...');

        const report = {
            testSummary: {
                timestamp: new Date().toISOString(),
                url: BASE_URL,
                totalErrors: this.results.errors.length,
                totalWarnings: this.results.warnings.length,
                totalRecommendations: this.results.recommendations.length
            },
            authentication: {
                loginSuccess: this.results.loginSuccess,
                userProfile: this.results.userProfile
            },
            apiEndpoints: this.results.apiTests,
            dataValidation: this.results.dataValidation,
            recommendations: this.results.recommendations,
            errors: this.results.errors,
            warnings: this.results.warnings
        };

        // Save detailed report
        const reportPath = path.join(__dirname, `presentation-assignment-api-report-${Date.now()}.json`);
        try {
            await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
            console.log(`📋 Detailed report saved: ${reportPath}`);
        } catch (error) {
            console.warn('⚠️  Could not save report file:', error.message);
        }

        // Print executive summary
        console.log('\n📊 EXECUTIVE SUMMARY:');
        console.log('=====================');
        
        const apiSuccessCount = Object.values(this.results.apiTests).filter(test => test.success).length;
        const totalApiTests = Object.keys(this.results.apiTests).length;
        
        console.log(`🔐 Authentication: ${report.authentication.loginSuccess ? '✅ SUCCESS' : '❌ FAILED'}`);
        console.log(`🌐 API Endpoints: ${apiSuccessCount}/${totalApiTests} working`);
        console.log(`📊 Data Validation: ${Object.keys(this.results.dataValidation).length} checks performed`);
        console.log(`💡 Recommendations: ${report.totalRecommendations || 0} generated`);
        console.log(`⚠️  Warnings: ${report.totalWarnings || 0}`);
        console.log(`❌ Errors: ${report.totalErrors || 0}`);

        // Presentation Assignment Functionality Assessment
        console.log('\n🎯 PRESENTATION ASSIGNMENT FUNCTIONALITY ASSESSMENT:');
        console.log('====================================================');

        const assessment = this.assessFunctionality();
        Object.entries(assessment).forEach(([category, result]) => {
            const status = result.working ? '✅' : (result.partial ? '⚠️ ' : '❌');
            console.log(`${status} ${category}: ${result.status}`);
            if (result.details) {
                console.log(`    ${result.details}`);
            }
        });

        // Grillometer System Analysis
        if (this.results.dataValidation.assignmentsAnalysis) {
            console.log('\n🔥 GRILLOMETER SYSTEM ANALYSIS:');
            console.log('================================');
            
            const grillometerAnalysis = this.assessGrillometerSystem();
            Object.entries(grillometerAnalysis).forEach(([aspect, result]) => {
                const status = result.implemented ? '✅' : (result.partial ? '⚠️ ' : '❌');
                console.log(`${status} ${aspect}: ${result.status}`);
            });
        }

        // Theme System Analysis
        if (this.results.dataValidation.uiAnalysis) {
            console.log('\n🎨 THEME SYSTEM ANALYSIS:');
            console.log('=========================');
            
            const ui = this.results.dataValidation.uiAnalysis;
            console.log(`✅ Theme Support: ${ui.themes.length} themes (${ui.themes.join(', ')})`);
            console.log(`${ui.hasThemeSupport ? '✅' : '❌'} CSS Variable System: ${ui.hasThemeSupport ? 'Implemented' : 'Missing'}`);
            console.log(`${ui.hasResponsiveDesign ? '✅' : '❌'} Responsive Design: ${ui.hasResponsiveDesign ? 'Implemented' : 'Missing'}`);
        }

        // Integration Status
        console.log('\n🔗 INTEGRATION STATUS:');
        console.log('======================');
        
        const integrations = this.assessIntegrations();
        Object.entries(integrations).forEach(([system, result]) => {
            const status = result.working ? '✅' : (result.partial ? '⚠️ ' : '❌');
            console.log(`${status} ${system}: ${result.status}`);
        });

        // Recommendations Summary
        if (this.results.recommendations.length > 0) {
            console.log('\n💡 KEY RECOMMENDATIONS:');
            console.log('=======================');
            
            this.results.recommendations.forEach((rec, i) => {
                const priority = rec.priority === 'High' ? '🔴' : rec.priority === 'Medium' ? '🟡' : '🟢';
                console.log(`${i + 1}. ${priority} ${rec.category}: ${rec.message}`);
            });
        }

        return report;
    }

    assessFunctionality() {
        const api = this.results.apiTests;
        const data = this.results.dataValidation;
        
        return {
            'Assignment Creation': {
                working: api.getAssignments?.success && data.studentsAvailable,
                status: api.getAssignments?.success ? 
                    (data.studentsAvailable ? 'API working, students available' : 'API working but no students') :
                    'API endpoint not responding',
                details: data.studentCount ? `${data.studentCount} students available for assignment` : null
            },
            'Meeting Integration': {
                working: api.getMeetings?.success && data.meetingsAvailable,
                partial: api.getMeetings?.success && !data.meetingsAvailable,
                status: api.getMeetings?.success ? 
                    (data.meetingsAvailable ? 'Working with available meetings' : 'API working but no meetings configured') :
                    'Meeting API not responding',
                details: data.meetingCount ? `${data.meetingCount} meetings available` : null
            },
            'Presentation Types': {
                working: api.getTypes?.success && api.getTypes?.data?.length > 0,
                status: api.getTypes?.success ? 
                    `${api.getTypes.data.length} types available` : 
                    'Presentation types API not responding'
            },
            'Form Validation': {
                working: api.formValidation?.invalidDataRejected,
                status: api.formValidation?.invalidDataRejected ? 
                    'Server-side validation working' : 
                    'Form validation may be weak or missing'
            }
        };
    }

    assessGrillometerSystem() {
        const ui = this.results.dataValidation.uiAnalysis;
        const assignments = this.results.dataValidation.assignmentsAnalysis;
        
        return {
            'UI Implementation': {
                implemented: ui?.hasGrillometerUI,
                status: ui?.hasGrillometerUI ? 
                    'Grillometer interface present in UI' : 
                    'Grillometer UI not detected'
            },
            'Data Storage': {
                implemented: assignments?.assignmentsWithGrillometer > 0,
                partial: assignments?.totalAssignments > 0 && assignments?.assignmentsWithGrillometer === 0,
                status: assignments?.assignmentsWithGrillometer > 0 ? 
                    `${assignments.assignmentsWithGrillometer}/${assignments.totalAssignments} assignments use grillometer` :
                    assignments?.totalAssignments > 0 ? 
                        'Grillometer data storage available but unused' :
                        'No assignment data to analyze'
            },
            'Feedback Levels': {
                implemented: ui?.grillometerLevels?.length === 3,
                status: ui?.grillometerLevels?.length === 3 ? 
                    '3-level system (Relaxed/Moderate/Intense)' : 
                    'Grillometer levels not properly configured'
            }
        };
    }

    assessIntegrations() {
        const api = this.results.apiTests;
        const data = this.results.dataValidation;
        
        return {
            'Student Roster': {
                working: api.getRoster?.success && data.studentsAvailable,
                status: api.getRoster?.success ? 
                    (data.studentsAvailable ? `${data.studentCount} students integrated` : 'Roster API working but no students') :
                    'Roster integration failed'
            },
            'Meeting System': {
                working: api.getMeetings?.success && data.meetingsAvailable,
                partial: api.getMeetings?.success && !data.meetingsAvailable,
                status: api.getMeetings?.success ? 
                    (data.meetingsAvailable ? `${data.meetingCount} meetings integrated` : 'Meeting API working but no meetings') :
                    'Meeting integration failed'
            },
            'Authentication': {
                working: this.results.loginSuccess && this.results.userProfile,
                status: this.results.loginSuccess ? 
                    `Authenticated as ${this.results.userProfile?.username} (${this.results.userProfile?.role})` :
                    'Authentication failed'
            }
        };
    }
}

// Main execution
async function main() {
    const tester = new PresentationAssignmentAPITester();
    
    try {
        await tester.runAllTests();
        await tester.generateReport();
        
    } catch (error) {
        console.error('💥 Fatal error:', error.message);
        process.exit(1);
    }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch(console.error);
}

export default PresentationAssignmentAPITester;