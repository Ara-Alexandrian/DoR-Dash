# Manual Test Instructions for Presentation Assignments

## Test Summary from API Analysis

✅ **Authentication**: Working properly with JWT tokens  
✅ **Presentation Types**: 7 types available (casual, mock_defense, pre_conference, thesis_proposal, dissertation_defense, journal_club, research_update)  
✅ **Meeting Integration**: 4 meetings available for assignment  
✅ **Form Validation**: Server-side validation working  
✅ **Grillometer System**: UI implemented with 3-level feedback system  
✅ **Theme Support**: 5 themes (light, dark, dracula, mbp, lsu)  
✅ **Responsive Design**: Implemented with Tailwind classes  

## Manual Testing Instructions

### 1. Login and Navigation
1. Go to https://dd.kronisto.net/login
2. Login with credentials: `cerebro` / `123`
3. Navigate to "Presentation Assignments" from the menu
4. **Expected**: Should see the presentation assignments page

### 2. Test Form Functionality (Faculty/Admin View)
If you have faculty/admin permissions, you should see:

#### Create Assignment Form
1. Click the "New Assignment" button
2. **Student Dropdown**: Should populate with available students
3. **Meeting Dropdown**: Should show 4 available meetings (optional field)
4. **Title Field**: Required field for assignment title
5. **Presentation Type**: Should show 7 types:
   - Casual Presentation
   - Mock Defense
   - Pre-Conference Practice
   - Thesis Proposal
   - Dissertation Defense
   - Journal Club
   - Research Update
6. **Duration**: Optional field (1-300 minutes)
7. **Due Date**: Optional date picker
8. **Description**: Multi-line text area
9. **Requirements**: Multi-line text area for specific requirements

#### Grillometer Settings
The form should include a grillometer section with:
- **Novelty Assessment**: 3 levels (Relaxed 🧊, Moderate 🔥, Intense 🔥🔥🔥)
- **Methodology Review**: 3 levels (same as above)
- **Presentation Delivery**: 3 levels (same as above)

**Test each grillometer setting** to ensure radio buttons work properly.

#### Form Actions
- **Cancel**: Should close the form without saving
- **Create Assignment**: Should validate required fields and create assignment

### 3. Test All 5 Themes
Test the page appearance with each theme:

1. **Light Theme**: Default light colors
2. **Dark Theme**: Dark background with light text
3. **Dracula Theme**: Purple/dark theme inspired by Dracula
4. **MBP Theme**: MBP College colors
5. **LSU Theme**: LSU colors

**For each theme, verify:**
- Text is readable against background
- Form elements are properly styled
- Grillometer icons are visible
- No visual glitches or color conflicts

### 4. Test Responsive Design
Test the page at different screen sizes:

1. **Desktop** (1366x768 or larger)
2. **Tablet** (768x1024)
3. **Mobile** (375x667)

**Verify:**
- Form layout adapts properly
- Buttons remain accessible
- Text remains readable
- No horizontal scrolling issues

### 5. Test Assignment Management
If assignments exist:

1. **View Assignments**: Check if existing assignments display properly
2. **Edit Assignment**: Click edit button on an assignment
3. **Complete/Incomplete**: Test toggling completion status
4. **Delete Assignment**: Test deletion (with confirmation)

### 6. Test Grillometer Display
If assignments have grillometer settings:

1. **Grillometer Icons**: Should show 🧊, 🔥, or 🔥🔥🔥 based on intensity
2. **Labels**: Should show "Relaxed", "Moderate", or "Intense"
3. **Categories**: Should display for Novelty, Methodology, and Delivery
4. **Faculty Notes**: Should be visible to faculty/admin only

### 7. Test Integration Features

#### Meeting Integration
- Assignments should optionally link to specific meetings
- Meeting titles and dates should display correctly

#### Student Assignment
- Students should only see their own assignments
- Faculty/admin should see all assignments

### 8. Test Error Handling
1. Try submitting form with missing required fields
2. Try accessing the page without proper permissions
3. Test with invalid data inputs

## Expected Results Summary

### What Should Work Well:
✅ **Authentication and Authorization**: Proper role-based access  
✅ **Form Validation**: Required fields enforced  
✅ **Grillometer System**: All 3 categories with 3 intensity levels  
✅ **Theme Switching**: All 5 themes should work smoothly  
✅ **Responsive Layout**: Should work on all device sizes  
✅ **Meeting Integration**: Should link assignments to meetings  
✅ **Presentation Types**: 7 different types available  

### Potential Issues to Watch For:
⚠️ **Student Roster**: May not populate if no students exist  
⚠️ **Empty State**: Page may appear empty if no assignments exist yet  
⚠️ **Permission Levels**: Ensure proper access control between student/faculty views  

## Grillometer System Details

The grillometer is the unique feedback intensity system:

### Purpose
Guide faculty on how intensively to review different aspects of presentations:
- **Novelty**: How critically to assess originality and innovation
- **Methodology**: How rigorously to examine research methods  
- **Delivery**: How critically to evaluate presentation skills

### Levels
1. **🧊 Relaxed**: Light feedback, developmental approach
2. **🔥 Moderate**: Standard academic review level
3. **🔥🔥🔥 Intense**: Rigorous, high-stakes evaluation

### Example Usage
A "3-2-1" assignment means:
- Focus intensely on **novelty** (🔥🔥🔥)
- Give moderate attention to **methodology** (🔥)
- Be relaxed about **delivery** (🧊) since student is still developing

This system helps standardize feedback expectations across faculty members.

## Theme System Details

### Available Themes:
1. **Light**: Standard light theme with good contrast
2. **Dark**: Professional dark theme for low-light environments
3. **Dracula**: Popular programmer theme with purple accents
4. **MBP**: MBP College branded colors and styling
5. **LSU**: Louisiana State University colors and branding

Each theme should maintain:
- Good contrast ratios for accessibility
- Consistent component styling
- Proper form element visibility
- Readable text at all sizes

## Reporting Issues

If you find any issues during testing:

1. **Screenshot the problem** 
2. **Note the theme being used**
3. **Record the browser and screen size**
4. **Document the steps to reproduce**
5. **Check browser console for errors**

The system has been designed with comprehensive error handling and responsive design, so most functionality should work smoothly across different environments.