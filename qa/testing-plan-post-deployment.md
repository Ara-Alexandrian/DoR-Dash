# DoR-Dash Post-Deployment Testing Plan

## Test Status: Ready for Execution
**Deployment Date**: 2025-06-26  
**Site URL**: https://dd.kronisto.net  
**Cache Busting Verified**: ✅ (Hashed filenames detected: `start.bb86582c.js`, `app.59820cbd.js`)

---

## 🎯 Test Objectives

Validate the recently implemented features:
1. **File Attachment System** for presentation assignments
2. **Dashboard Improvements** (presenter names, meeting links)
3. **Meeting Agenda Integration** with file display/download
4. **Browser Cache Busting** system
5. **Assignment Navigation Links** throughout the application

---

## 🧪 Test Scenarios

### **1. Cache Busting System Verification**
**Status**: ✅ **PASSED** - Hashed filenames detected
- [x] Asset files have unique hashes (e.g., `start.bb86582c.js`)
- [ ] User notification appears for new builds (requires rebuild test)
- [ ] Force refresh clears cache properly

### **2. Login and Authentication**
**Test Data**: Use existing credentials
```
Login URL: https://dd.kronisto.net/login
Expected: Redirect to dashboard after successful login
```

**Test Steps**:
1. Navigate to https://dd.kronisto.net
2. Should redirect to login page
3. Enter valid credentials
4. Verify dashboard loads with user-specific content

### **3. Dashboard Presentation Assignment Display**
**Objective**: Verify presenter names show correctly (not assigner names)

**Test Steps**:
1. Login and navigate to dashboard
2. Locate "Presentation Assignments" section
3. **Expected**: Assignment shows "Nathan Dobranski" (presenter) not "Ara Alexandrian" (assigner)
4. **Expected**: Meeting link displayed instead of due date
5. **Expected**: File upload interface visible for assigned presenters

### **4. Presentation Assignment Detail Page**
**Test URL**: `https://dd.kronisto.net/presentation-assignments/[id]`

**Test Steps**:
1. Navigate to any presentation assignment
2. **Expected**: File upload section visible
3. **Expected**: Drag-and-drop functionality works
4. **Expected**: Only assigned presenter can upload files
5. Test file upload process (PDF/PowerPoint)
6. Verify file download functionality

### **5. Meeting Agenda Integration**
**Test URL**: `https://dd.kronisto.net/agenda/[meeting-id]`

**Test Steps**:
1. Navigate to a meeting agenda with presentation assignments
2. **Expected**: "Assigned Presentations" section visible
3. **Expected**: "Load Files" button for each assignment
4. Click "Load Files" and verify file display
5. Test file download links
6. **Expected**: Assignment titles are clickable links
7. **Expected**: Presenter names in schedule are clickable

### **6. File Upload Permissions**
**Security Test**: Verify only correct users can upload

**Test Steps**:
1. Login as faculty/admin (assignment creator)
2. Navigate to presentation assignment detail
3. **Expected**: NO file upload interface visible
4. Login as assigned student/presenter
5. **Expected**: File upload interface IS visible
6. Test upload functionality

### **7. Navigation Link Validation**
**Test Integration**: Verify links between agenda and assignments

**Test Locations**:
- Meeting agenda → Assignment detail pages
- Dashboard → Assignment detail pages  
- Assignment detail → Meeting agenda (if linked)

---

## 🤖 Automated Testing Commands

### Using Browser Developer Tools
```javascript
// Test cache busting detection
console.log('Cache buster initialized:', typeof window.cacheBuster !== 'undefined');

// Test file upload interface
document.querySelector('[type="file"]') !== null ? 'File upload found' : 'No file upload';

// Test assignment links in agenda
document.querySelectorAll('a[href*="/presentation-assignments/"]').length + ' assignment links found';
```

### Using curl for API Testing
```bash
# Test presentation assignment API
curl -H "Authorization: Bearer [token]" https://dd.kronisto.net/api/v1/presentation-assignments/

# Test file upload endpoint
curl -X POST -H "Authorization: Bearer [token]" -F "file=@test.pdf" https://dd.kronisto.net/api/v1/presentation-assignments/1/files/
```

---

## 🔍 Expected Results

### **Dashboard**
- ✅ Presentation assignments show presenter names (e.g., "Nathan Dobranski")
- ✅ Meeting links displayed instead of due dates
- ✅ File upload interface visible for assigned presenters only

### **Presentation Assignment Pages**
- ✅ Drag-and-drop file upload interface
- ✅ File list with download links
- ✅ Proper permission enforcement (only assigned presenter can upload)

### **Meeting Agendas** 
- ✅ "Presentation Materials" section for each assignment
- ✅ "Load Files" functionality
- ✅ File download links
- ✅ Assignment navigation links

### **Navigation**
- ✅ Assignment titles link to detail pages
- ✅ Presenter names link to assignments
- ✅ "View Details" links in file sections

---

## 🚨 Known Issues to Verify

1. **Edit Button Redirect**: Previously mentioned issue where edit buttons redirect to old edit page instead of inline solution
2. **File Upload Performance**: Large file upload handling
3. **Mobile Responsiveness**: Touch-friendly file upload on mobile devices

---

## 📊 Test Execution Checklist

### Pre-Test Setup
- [ ] Ensure test user accounts exist
- [ ] Prepare test files (PDF, PowerPoint, etc.)
- [ ] Document current presentation assignments in system

### Core Functionality Tests
- [ ] Login and dashboard verification
- [ ] Presentation assignment display verification
- [ ] File upload functionality
- [ ] File download functionality
- [ ] Permission system validation
- [ ] Meeting agenda integration
- [ ] Navigation link verification

### Browser Compatibility
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari (if available)
- [ ] Mobile browsers

### Performance Tests
- [ ] Page load times
- [ ] File upload speed
- [ ] Large file handling
- [ ] Multiple concurrent uploads

---

## 🐛 Issue Reporting Template

```markdown
**Issue**: [Brief description]
**URL**: [Specific page URL]
**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Result**: [What should happen]
**Actual Result**: [What actually happened]
**Browser**: [Chrome/Firefox/Safari + version]
**User Role**: [Admin/Faculty/Student]
**Screenshots**: [If applicable]
```

---

## ✅ Success Criteria

The deployment is considered successful when:

1. **File System**: Users can upload and download presentation files
2. **Dashboard**: Correct presenter information displayed
3. **Agenda Integration**: Files accessible from meeting agendas
4. **Navigation**: Seamless links between agendas and assignments
5. **Permissions**: Proper role-based access control
6. **Cache Busting**: New builds automatically detected
7. **No Regressions**: Existing functionality remains intact

---

## 📞 Next Steps After Testing

1. **Document Results**: Update this file with actual test results
2. **Report Issues**: Create tickets for any bugs found
3. **User Training**: Notify users of new features
4. **Monitor Usage**: Track file upload/download metrics
5. **Gather Feedback**: Collect user feedback on new functionality

---

**Testing Contact**: Generated by Claude Code  
**Last Updated**: 2025-06-26  
**Test Environment**: Production (dd.kronisto.net)