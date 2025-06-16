<script>
  import { auth } from '$lib/stores/auth';
  import { updateApi, fileApi, apiFetch } from '$lib/api';
  import { facultyUpdateApi } from '$lib/api/faculty-updates';
  import { meetingsApi } from '$lib/api/meetings';
  import { onMount, tick } from 'svelte';
  import { goto } from '$app/navigation';
  import { get } from 'svelte/store';
  import { page } from '$app/stores';
  
  // API configuration
  const API_URL = import.meta.env.VITE_API_URL || '';
  const API_BASE = API_URL ? `${API_URL}/api/v1` : '/api/v1';
  
  // Check if user is faculty
  const isFaculty = $auth?.user?.role === 'faculty' || $auth?.user?.role === 'admin';
  
  // Student form data
  let progressText = '';
  let challengesText = '';
  let goalsText = '';
  let meetingNotes = '';
  let files = [];
  let isPresenting = false;
  let selectedMeeting = null;
  
  // Faculty form data
  let announcementsText = '';
  let projectsText = '';
  let projectStatusText = '';
  let facultyQuestions = '';
  let facultyIsPresenting = false;
  let facultyFiles = [];
  let announcementType = 'general'; // general, urgent, deadline
  
  // UI state
  let isSubmitting = false;
  let isLoading = true; // Add loading state for initial data
  let error = '';
  let success = '';
  let meetings = [];
  
  // Edit mode state
  let isEditMode = false;
  let editingUpdateId = null;
  let loadedUpdate = null;
  
  // Text refinement state
  let isRefining = false;
  let currentField = '';
  let refinementResult = null;
  let refinementPosition = { x: 0, y: 0 };
  let refinementTarget = null;
  let isEditingRefinement = false;
  let editedRefinedText = '';
  
  // Feedback system state
  let showFeedbackBox = false;
  let feedbackText = '';
  let feedbackType = 'improvement'; // 'improvement', 'error', 'suggestion'
  let isSubmittingFeedback = false;
  let feedbackSuccess = false;
  let lastRefinementId = null;
  
  // General feedback state
  let showGeneralFeedback = false;
  let generalFeedbackType = '';
  let generalFeedbackText = '';
  let isSubmittingGeneralFeedback = false;
  let generalFeedbackSuccess = false;
  
  // Star rating state
  let textQualityRating = 0;
  let textQualityHover = 0;
  let helpfulnessRating = 0;
  let helpfulnessHover = 0;
  let easeOfUseRating = 0;
  let easeOfUseHover = 0;
  
  // Custom feedback text
  let customFeedbackText = '';
  
  // Function to populate form fields from loaded update
  async function populateForm(update) {
    console.log('Populating form with update data:', update);
    
    // Wait for any pending DOM updates
    await tick();
    
    if (update.is_faculty) {
      // Faculty form - populate from loaded data
      announcementsText = update.announcements_text || '';
      projectsText = update.projects_text || '';
      projectStatusText = update.project_status_text || '';
      facultyQuestions = update.faculty_questions || '';
      announcementType = update.announcement_type || 'general';
      facultyIsPresenting = update.is_presenting || false;
      console.log('Populated faculty form:', {
        announcementsText, projectsText, projectStatusText, 
        facultyQuestions, announcementType, facultyIsPresenting
      });
    } else {
      // Student form - populate from loaded data
      progressText = update.progress_text || '';
      challengesText = update.challenges_text || '';
      goalsText = update.next_steps_text || '';
      meetingNotes = update.meeting_notes || '';
      isPresenting = update.will_present || false;
      console.log('Populated student form:', {
        progressText, challengesText, goalsText, meetingNotes, isPresenting
      });
    }
    selectedMeeting = update.meeting_id;
    console.log('Selected meeting:', selectedMeeting);
    
    // Force DOM update
    await tick();
    
    // Debug: Check if DOM elements exist and have values
    const progressEl = document.getElementById('progress');
    const challengesEl = document.getElementById('challenges');
    const goalsEl = document.getElementById('goals');
    
    console.log('DOM elements after population:', {
      progressEl: progressEl?.value,
      challengesEl: challengesEl?.value,
      goalsEl: goalsEl?.value,
      progressText,
      challengesText,
      goalsText
    });
    
    // Force update DOM values if they don't match
    if (progressEl && progressEl.value !== progressText) {
      progressEl.value = progressText;
      console.log('Manually set progress field value');
    }
    if (challengesEl && challengesEl.value !== challengesText) {
      challengesEl.value = challengesText;
      console.log('Manually set challenges field value');
    }
    if (goalsEl && goalsEl.value !== goalsText) {
      goalsEl.value = goalsText;
      console.log('Manually set goals field value');
    }
  }
  
  // Function to handle text refinement
  async function refineText(field, event) {
    let textToRefine = '';
    
    // Determine which field to refine
    switch(field) {
      // Student fields
      case 'progress':
        textToRefine = progressText;
        break;
      case 'challenges':
        textToRefine = challengesText;
        break;
      case 'goals':
        textToRefine = goalsText;
        break;
      case 'meetingNotes':
        textToRefine = meetingNotes;
        break;
      
      // Faculty fields
      case 'announcements':
        textToRefine = announcementsText;
        break;
      case 'projects':
        textToRefine = projectsText;
        break;
      case 'projectStatus':
        textToRefine = projectStatusText;
        break;
      case 'facultyQuestions':
        textToRefine = facultyQuestions;
        break;
      default:
        return;
    }
    
    // Check if text is empty
    if (!textToRefine.trim()) {
      error = 'Please enter some text to refine';
      setTimeout(() => error = '', 3000);
      return;
    }
    
    // Calculate position for the floating widget
    if (event && event.target) {
      const rect = event.target.getBoundingClientRect();
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
      const widgetWidth = 320; // 80 * 4 (w-80 in Tailwind)
      
      // Calculate initial position to the right of the button
      let x = rect.right + scrollLeft + 20;
      let y = rect.top + scrollTop;
      
      // If the widget would go off the right edge, position it to the left instead
      if (x + widgetWidth > window.innerWidth) {
        x = rect.left + scrollLeft - widgetWidth - 20;
      }
      
      // Ensure it doesn't go off the left edge
      if (x < 10) {
        x = 10;
      }
      
      // Ensure it doesn't go off the top
      if (y < 10) {
        y = 10;
      }
      
      refinementPosition = { x, y };
      refinementTarget = event.target.closest('.space-y-2');
    }
    
    currentField = field;
    isRefining = true;
    error = '';
    refinementResult = null;
    
    try {
      // Determine context based on field type
      let context = '';
      switch(field) {
        case 'progress':
          context = 'research_progress';
          break;
        case 'challenges':
          context = 'challenges';
          break;
        case 'goals':
          context = 'goals';
          break;
        case 'announcements':
          context = 'announcements';
          break;
        case 'projects':
        case 'projectStatus':
          context = 'research_progress';
          break;
        case 'meetingNotes':
        case 'facultyQuestions':
        default:
          context = 'general';
          break;
      }
      
      // Call enhanced text refinement API with context
      const response = await updateApi.refineText(textToRefine, context);
      refinementResult = response;
      
      // Show brief success message with word count improvement
      const wordDiff = response.word_count_refined - response.word_count_original;
      const diffText = wordDiff > 0 ? `+${wordDiff} words` : wordDiff < 0 ? `${wordDiff} words` : 'same length';
      success = `Text refinement complete (${diffText})`;
      setTimeout(() => success = '', 3000);
    } catch (err) {
      error = err.message || 'Failed to refine text. Please try again.';
    } finally {
      isRefining = false;
    }
  }
  
  // Function to start editing the refined text
  function startEditingRefinement() {
    isEditingRefinement = true;
    editedRefinedText = refinementResult.refined_text || refinementResult.refined || '';
  }
  
  // Function to save the edited refined text
  function saveEditedRefinement() {
    if (refinementResult) {
      refinementResult.refined_text = editedRefinedText;
      refinementResult.refined = editedRefinedText; // Fallback
    }
    isEditingRefinement = false;
  }
  
  // Function to cancel editing
  function cancelEditingRefinement() {
    isEditingRefinement = false;
    editedRefinedText = '';
  }
  
  // Feedback system functions
  function showFeedback() {
    showFeedbackBox = true;
    feedbackText = '';
    feedbackType = 'improvement';
    feedbackSuccess = false;
    // Store reference to the last refinement for context
    lastRefinementId = Date.now();
  }
  
  function hideFeedback() {
    showFeedbackBox = false;
    feedbackText = '';
    feedbackSuccess = false;
  }
  
  async function submitFeedback() {
    // Allow submission even without detailed text, as feedback type is sufficient
    if (!feedbackType) {
      error = 'Please select a feedback type';
      return;
    }
    
    isSubmittingFeedback = true;
    error = '';
    
    try {
      const feedbackData = {
        feedback_text: feedbackText.trim(),
        feedback_type: feedbackType,
        context: {
          field: currentField,
          original_text: refinementResult?.original_text || '',
          refined_text: refinementResult?.refined_text || '',
          user_field_type: currentField,
          improvement_suggestions: refinementResult?.suggestions || []
        },
        timestamp: new Date().toISOString(),
        user_context: {
          is_faculty: isFaculty,
          user_role: $auth.user?.role || 'student'
        }
      };
      
      // Submit feedback to knowledge base
      const response = await fetch('/api/v1/text/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${$auth.token}`
        },
        body: JSON.stringify(feedbackData)
      });
      
      if (!response.ok) {
        throw new Error('Failed to submit feedback');
      }
      
      feedbackSuccess = true;
      success = 'Thank you! Your feedback will help improve the text refinement feature.';
      setTimeout(() => {
        hideFeedback();
        success = '';
      }, 3000);
      
    } catch (err) {
      error = err.message || 'Failed to submit feedback. Please try again.';
    } finally {
      isSubmittingFeedback = false;
    }
  }
  
  // General feedback submission function
  async function submitGeneralFeedback() {
    if (!generalFeedbackType) {
      error = 'Please select your experience level';
      return;
    }
    
    isSubmittingGeneralFeedback = true;
    error = '';
    
    try {
      const feedbackData = {
        feedback_text: generalFeedbackText.trim(),
        feedback_type: generalFeedbackType,
        context: {
          field: 'general_experience',
          feedback_category: 'general_ai_refinement',
          usage_context: 'submission_form'
        },
        timestamp: new Date().toISOString(),
        user_context: {
          is_faculty: isFaculty,
          user_role: $auth.user?.role || 'student'
        }
      };
      
      // Submit general feedback
      const response = await fetch('/api/v1/text/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${$auth.token}`
        },
        body: JSON.stringify(feedbackData)
      });
      
      if (!response.ok) {
        throw new Error('Failed to submit feedback');
      }
      
      generalFeedbackSuccess = true;
      setTimeout(() => {
        generalFeedbackSuccess = false;
        generalFeedbackText = '';
        generalFeedbackType = '';
      }, 3000);
      
    } catch (err) {
      error = err.message || 'Failed to submit feedback. Please try again.';
    } finally {
      isSubmittingGeneralFeedback = false;
    }
  }
  
  // Function to apply refined text
  function applyRefinedText() {
    if (!refinementResult) return;
    
    // Use the edited text if available, otherwise use the original refined text
    const textToApply = isEditingRefinement ? editedRefinedText : (refinementResult.refined_text || refinementResult.refined);
    
    switch(currentField) {
      // Student fields
      case 'progress':
        progressText = textToApply;
        break;
      case 'challenges':
        challengesText = textToApply;
        break;
      case 'goals':
        goalsText = textToApply;
        break;
      case 'meetingNotes':
        meetingNotes = textToApply;
        break;
      
      // Faculty fields
      case 'announcements':
        announcementsText = textToApply;
        break;
      case 'projects':
        projectsText = textToApply;
        break;
      case 'projectStatus':
        projectStatusText = textToApply;
        break;
      case 'facultyQuestions':
        facultyQuestions = textToApply;
        break;
    }
    
    // Clear refinement result after applying
    refinementResult = null;
    isEditingRefinement = false;
    editedRefinedText = '';
  }
  
  // Handle form submission
  async function handleSubmit() {
    // Different validation and submission based on user role
    if (isFaculty) {
      // Faculty form validation
      if (!announcementsText.trim() && !projectsText.trim()) {
        error = 'Please provide either announcements or project updates';
        return;
      }
      
      if (!selectedMeeting) {
        error = 'Please select a meeting for your update';
        return;
      }
      
      // Validate file upload requirement for faculty presentations
      if (facultyIsPresenting && (!facultyFiles || facultyFiles.length === 0)) {
        error = 'Please attach your presentation materials before submitting';
        return;
      }
      
      isSubmitting = true;
      error = '';
      
      try {
        // Create faculty update object
        const updateData = {
          is_faculty: true,
          user_id: $auth.user?.id,
          user_name: $auth.user?.full_name || $auth.user?.username,
          announcements_text: announcementsText,
          announcement_type: announcementType,
          projects_text: projectsText,
          project_status_text: projectStatusText,
          faculty_questions: facultyQuestions,
          is_presenting: facultyIsPresenting,
          meeting_id: selectedMeeting
        };
        
        // Store feedback data to submit AFTER successful update creation
        let pendingFeedbackData = null;
        if (textQualityRating > 0 || helpfulnessRating > 0 || easeOfUseRating > 0 || customFeedbackText.trim()) {
          pendingFeedbackData = {
            feedback_text: customFeedbackText.trim() || 'Star ratings only',
            feedback_type: 'comprehensive_submission_feedback',
            context: {
              field: 'general_submission',
              feedback_category: 'submission_feedback',
              // Star ratings for quantitative analysis
              text_quality_rating: textQualityRating,
              helpfulness_rating: helpfulnessRating,
              ease_of_use_rating: easeOfUseRating,
              // Custom feedback for qualitative analysis
              custom_feedback: customFeedbackText.trim(),
              // Submission context for LoRA training
              submission_type: 'faculty_update',
              usage_context: 'faculty_submission_form',
              // Content context for training data
              content_fields: {
                announcements_text: announcementsText,
                projects_text: projectsText,
                project_status_text: projectStatusText,
                faculty_questions: facultyQuestions
              },
              meeting_id: selectedMeeting,
              is_presenting: facultyIsPresenting
            },
            timestamp: new Date().toISOString(),
            user_context: {
              is_faculty: true,
              user_role: 'faculty',
              user_id: $auth.user?.id
            }
          };
        }
        
        console.log('Submitting faculty update:', updateData);
        
        // Submit faculty update
        let update;
        if (isEditMode && editingUpdateId) {
          // Update existing faculty update using proper API
          update = await facultyUpdateApi.updateFacultyUpdate(editingUpdateId, updateData);
          console.log('Faculty update updated successfully:', update);
        } else {
          // Create new faculty update
          update = await facultyUpdateApi.createUpdate(updateData);
          console.log('Faculty update created successfully:', update);
        }
        
        // Upload files if any
        if (facultyFiles.length > 0) {
          console.log(`Uploading ${facultyFiles.length} files for faculty update:`, Array.from(facultyFiles).map(f => f.name));
          
          try {
            // Upload files to the created faculty update
            const formData = new FormData();
            for (let i = 0; i < facultyFiles.length; i++) {
              formData.append('files', facultyFiles[i]);
            }
            
            const authStore = get(auth);
            const response = await fetch(`${API_BASE}/faculty-updates/${update.id}/files`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${authStore.token}`
              },
              body: formData
            });
            
            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'File upload failed');
            }
            
            const uploadResult = await response.json();
            console.log('Faculty files uploaded successfully:', uploadResult);
          } catch (fileError) {
            console.error('Faculty file upload failed:', fileError);
            // Don't fail the entire submission for file upload errors
            error = `Faculty update submitted but file upload failed: ${fileError.message}`;
          }
        }
        
        // Submit feedback with submission ID for LoRA training dataset
        if (pendingFeedbackData && update?.id) {
          try {
            // Add submission ID to feedback for training data linking
            pendingFeedbackData.context.submission_id = update.id;
            pendingFeedbackData.context.submission_data = updateData;
            
            await fetch('/api/v1/text/feedback', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${$auth.token}`
              },
              body: JSON.stringify(pendingFeedbackData)
            });
            console.log('Feedback submitted with submission ID:', update.id);
          } catch (feedbackError) {
            console.log('Feedback submission failed:', feedbackError);
          }
        }
        
        // Show success and redirect
        success = 'Your faculty update has been submitted successfully!';
        setTimeout(() => {
          goto('/dashboard');
        }, 2000);
        
      } catch (err) {
        error = err.message || 'Failed to submit faculty update. Please try again.';
      } finally {
        isSubmitting = false;
      }
    } else {
      // Student form validation
      if (!progressText.trim()) {
        error = 'Please describe your progress';
        return;
      }
      
      if (!selectedMeeting) {
        error = 'Please select a meeting for your update';
        return;
      }
      
      // Note: File upload is optional, but if files are selected we'll try to upload them
      
      isSubmitting = true;
      error = '';
      
      try {
        // Get current user ID
        const currentUser = get(auth).user;
        
        // Create student update object matching backend schema
        const updateData = {
          user_id: currentUser.id,
          progress_text: progressText,
          challenges_text: challengesText || '',
          next_steps_text: goalsText || '',
          meeting_notes: meetingNotes || '',
          will_present: isPresenting,
          meeting_id: selectedMeeting
        };
        
        // Store feedback data to submit AFTER successful update creation
        let pendingStudentFeedbackData = null;
        if (textQualityRating > 0 || helpfulnessRating > 0 || easeOfUseRating > 0 || customFeedbackText.trim()) {
          pendingStudentFeedbackData = {
            feedback_text: customFeedbackText.trim() || 'Star ratings only',
            feedback_type: 'comprehensive_submission_feedback',
            context: {
              field: 'general_submission',
              feedback_category: 'submission_feedback',
              // Star ratings for quantitative analysis
              text_quality_rating: textQualityRating,
              helpfulness_rating: helpfulnessRating,
              ease_of_use_rating: easeOfUseRating,
              // Custom feedback for qualitative analysis
              custom_feedback: customFeedbackText.trim(),
              // Submission context for LoRA training
              submission_type: 'student_update',
              usage_context: 'student_submission_form',
              // Content context for training data
              content_fields: {
                progress_text: progressText,
                challenges_text: challengesText,
                next_steps_text: goalsText,
                meeting_notes: meetingNotes
              },
              meeting_id: selectedMeeting,
              will_present: isPresenting
            },
            timestamp: new Date().toISOString(),
            user_context: {
              is_faculty: false,
              user_role: currentUser.role || 'student',
              user_id: currentUser.id
            }
          };
        }
        
        // Submit update using the correct endpoint
        let update;
        if (isEditMode && editingUpdateId) {
          // Update existing update
          update = await updateApi.updateUpdate(editingUpdateId, updateData);
          console.log('Student update updated successfully:', update);
        } else {
          // Create new update
          update = await apiFetch('/updates/', {
            method: 'POST',
            body: JSON.stringify(updateData)
          });
          console.log('Student update created successfully:', update);
        }
        
        // Upload files if any
        if (files.length > 0) {
          console.log(`Uploading ${files.length} files:`, Array.from(files).map(f => f.name));
          
          try {
            // Upload files to the created update
            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
              formData.append('files', files[i]);
            }
            
            const authStore = get(auth);
            const response = await fetch(`${API_BASE}/updates/${update.id}/files`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${authStore.token}`
              },
              body: formData
            });
            
            if (!response.ok) {
              const error = await response.json();
              throw new Error(error.detail || 'File upload failed');
            }
            
            const uploadResult = await response.json();
            console.log('Files uploaded successfully:', uploadResult);
          } catch (fileError) {
            console.error('File upload failed:', fileError);
            // Don't fail the entire submission for file upload errors
            error = `Update submitted but file upload failed: ${fileError.message}`;
          }
        }
        
        // Submit feedback with submission ID for LoRA training dataset
        if (pendingStudentFeedbackData && update?.id) {
          try {
            // Add submission ID to feedback for training data linking
            pendingStudentFeedbackData.context.submission_id = update.id;
            pendingStudentFeedbackData.context.submission_data = updateData;
            
            await fetch('/api/v1/text/feedback', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${$auth.token}`
              },
              body: JSON.stringify(pendingStudentFeedbackData)
            });
            console.log('Student feedback submitted with submission ID:', update.id);
          } catch (feedbackError) {
            console.log('Student feedback submission failed:', feedbackError);
          }
        }
        
        // Show success and redirect
        if (isEditMode) {
          success = 'Your update has been updated successfully!';
          setTimeout(() => {
            goto('/updates');
          }, 2000);
        } else {
          success = 'Your update has been submitted successfully!';
          setTimeout(() => {
            goto('/dashboard');
          }, 2000);
        }
        
      } catch (err) {
        error = err.message || 'Failed to submit update. Please try again.';
      } finally {
        isSubmitting = false;
      }
    }
  }
  
  // File validation and size formatting
  function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
  
  function validateFiles(fileList) {
    const validFiles = [];
    const errors = [];
    const maxSize = 50 * 1024 * 1024; // 50MB
    const maxFiles = 20;
    
    if (fileList.length > maxFiles) {
      errors.push(`Maximum ${maxFiles} files allowed`);
      return { validFiles: [], errors };
    }
    
    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i];
      
      if (file.size > maxSize) {
        errors.push(`${file.name} exceeds 50MB limit (${formatFileSize(file.size)})`);
        continue;
      }
      
      if (!file.name || file.name.trim() === '') {
        errors.push('File has invalid name');
        continue;
      }
      
      validFiles.push(file);
    }
    
    return { validFiles, errors };
  }
  
  // Handle file input change for students
  function handleFileChange(event) {
    const fileList = Array.from(event.target.files || []);
    const { validFiles, errors } = validateFiles(fileList);
    
    if (errors.length > 0) {
      error = errors.join('; ');
      setTimeout(() => error = '', 5000);
    } else {
      error = '';
    }
    
    files = validFiles;
  }
  
  // Handle file input change for faculty
  function handleFacultyFileChange(event) {
    const fileList = Array.from(event.target.files || []);
    const { validFiles, errors } = validateFiles(fileList);
    
    if (errors.length > 0) {
      error = errors.join('; ');
      setTimeout(() => error = '', 5000);
    } else {
      error = '';
    }
    
    facultyFiles = validFiles;
  }
  
  // Load upcoming meetings
  onMount(async () => {
    isLoading = true; // Set loading state
    try {
      // Check if we're in edit mode
      const editId = $page.url.searchParams.get('edit');
      const updateType = $page.url.searchParams.get('type');
      
      if (editId) {
        isEditMode = true;
        editingUpdateId = editId;
        
        try {
          let update;
          if (updateType === 'faculty') {
            // Load faculty update data using the proper API function
            update = await facultyUpdateApi.getFacultyUpdate(editId);
            update.is_faculty = true; // Mark as faculty update
          } else {
            // Load student update data
            update = await updateApi.getUpdate(editId);
            update.is_faculty = false; // Mark as student update
          }
          
          console.log('Loaded update data in onMount:', update);
          loadedUpdate = update;
          
          // Populate form immediately after loading
          await populateForm(update);
        } catch (err) {
          console.error('Failed to load update for editing:', err);
          error = `Failed to load update data: ${err.message}. Please try again.`;
          // Don't continue loading if edit data failed
          isLoading = false;
          return;
        }
      }
      
      // Get upcoming meetings
      const today = new Date();
      const threeMonthsFromNow = new Date();
      threeMonthsFromNow.setMonth(today.getMonth() + 3);
      
      try {
        meetings = await meetingsApi.getMeetings({
          start_date: today.toISOString(),
          end_date: threeMonthsFromNow.toISOString()
        });
      } catch (err) {
        console.warn('Failed to load meetings:', err);
        meetings = []; // No fallback demo data
      }
    } catch (err) {
      console.error('Error loading page:', err);
    } finally {
      isLoading = false; // Clear loading state
    }
  });
  
  // Format date and time for display
  function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    }) + ' ' + date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }
</script>

<div class="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900">
      {#if isEditMode}
        Edit Update
      {:else if isFaculty}
        Submit Faculty Update
      {:else}
        Submit Student Update
      {/if}
    </h1>
    <p class="mt-2 text-gray-600">
      {#if isFaculty}
        Share announcements, project updates, and meeting plans. Use the AI-powered "Refine & Proofread" 
        button to improve the clarity and quality of your text.
      {:else}
        Share your research progress, challenges, and upcoming goals. Use the AI-powered "Refine & Proofread" 
        button to improve the clarity and quality of your text.
      {/if}
    </p>
    <div class="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-md">
      <div class="flex">
        <svg class="h-5 w-5 text-blue-600 mr-2 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div class="text-sm text-blue-800">
          <p><strong>Required fields are marked with *</strong></p>
          <p class="mt-1">
            {#if isFaculty}
              • At least one content section (announcements OR projects) • Meeting selection
            {:else}
              • At least one content section (progress OR challenges OR goals) • Meeting selection
            {/if}
            {#if isPresenting || facultyIsPresenting}
              • File attachments (required for presentations)
            {/if}
          </p>
        </div>
      </div>
    </div>
  </div>
  
  {#if error}
    <div class="mb-6 p-4 bg-red-50 rounded-md">
      <p class="text-sm text-red-700">{error}</p>
    </div>
  {/if}
  
  {#if success}
    <div class="mb-6 p-4 bg-green-50 rounded-md">
      <p class="text-sm text-green-700">{success}</p>
    </div>
  {/if}
  
  {#if isLoading}
    <div class="text-center py-10">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
      <p class="mt-2 text-gray-500">Loading update data...</p>
    </div>
  {:else}
  <form on:submit|preventDefault={handleSubmit} class="space-y-6">
    {#if isFaculty}
      <!-- FACULTY FORM -->
      
      <!-- Announcements section -->
      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <label for="announcements" class="block text-sm font-medium text-gray-700">
            Group Announcements <span class="text-gray-400">(at least one section required *)</span>
          </label>
          <button 
            type="button"
            class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-sm font-medium rounded-lg shadow-sm hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            on:click={(e) => refineText('announcements', e)}
            disabled={isRefining || isSubmitting}
            title="AI-powered text enhancement using domain-specific knowledge"
          >
            {#if isRefining && currentField === 'announcements'}
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              AI Refining...
            {:else}
              <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.414 10.5H9v-1.5z" />
              </svg>
              ✨ Refine & Proofread
            {/if}
          </button>
        </div>
        <textarea
          id="announcements"
          rows="5"
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
          placeholder="Share announcements, deadlines, or important information for all students..."
          bind:value={announcementsText}
          disabled={isSubmitting}
        ></textarea>
        
        <!-- Announcement type selection -->
        <div class="mt-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Announcement Type</label>
          <div class="flex space-x-4">
            <label class="inline-flex items-center">
              <input 
                type="radio" 
                class="form-radio text-primary-600" 
                name="announcementType" 
                value="general"
                bind:group={announcementType}
                disabled={isSubmitting}
              />
              <span class="ml-2 text-sm text-gray-700">General</span>
            </label>
            <label class="inline-flex items-center">
              <input 
                type="radio" 
                class="form-radio text-red-600" 
                name="announcementType" 
                value="urgent"
                bind:group={announcementType}
                disabled={isSubmitting}
              />
              <span class="ml-2 text-sm text-gray-700">Urgent</span>
            </label>
            <label class="inline-flex items-center">
              <input 
                type="radio" 
                class="form-radio text-yellow-600" 
                name="announcementType" 
                value="deadline"
                bind:group={announcementType}
                disabled={isSubmitting}
              />
              <span class="ml-2 text-sm text-gray-700">Deadline</span>
            </label>
          </div>
        </div>
      </div>
      
      <!-- Projects section -->
      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <label for="projects" class="block text-sm font-medium text-gray-700">
            Current Projects
          </label>
          <button 
            type="button"
            class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-sm font-medium rounded-lg shadow-sm hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            title="AI-powered text enhancement using domain-specific knowledge"
            on:click={(e) => refineText('projects', e)}
            disabled={isRefining || isSubmitting}
          >
            {#if isRefining && currentField === 'projects'}
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              AI Refining...
            {:else}
              <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.414 10.5H9v-1.5z" />
              </svg>
              ✨ Refine & Proofread
            {/if}
          </button>
        </div>
        <textarea
          id="projects"
          rows="4"
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
          placeholder="Describe current research projects and initiatives you're working on..."
          bind:value={projectsText}
          disabled={isSubmitting}
        ></textarea>
      </div>
      
      <!-- Project Status section -->
      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <label for="projectStatus" class="block text-sm font-medium text-gray-700">
            Project Status Updates
          </label>
          <button 
            type="button"
            class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-sm font-medium rounded-lg shadow-sm hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            title="AI-powered text enhancement using domain-specific knowledge"
            on:click={(e) => refineText('projectStatus', e)}
            disabled={isRefining || isSubmitting}
          >
            {#if isRefining && currentField === 'projectStatus'}
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              AI Refining...
            {:else}
              <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.414 10.5H9v-1.5z" />
              </svg>
              ✨ Refine & Proofread
            {/if}
          </button>
        </div>
        <textarea
          id="projectStatus"
          rows="4"
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
          placeholder="Share updates on the status of current projects, grants, or initiatives..."
          bind:value={projectStatusText}
          disabled={isSubmitting}
        ></textarea>
      </div>
      
      <!-- Faculty Questions section -->
      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <label for="facultyQuestions" class="block text-sm font-medium text-gray-700">
            Questions for Students
          </label>
          <button 
            type="button"
            class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-sm font-medium rounded-lg shadow-sm hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            title="AI-powered text enhancement using domain-specific knowledge"
            on:click={(e) => refineText('facultyQuestions', e)}
            disabled={isRefining || isSubmitting}
          >
            {#if isRefining && currentField === 'facultyQuestions'}
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              AI Refining...
            {:else}
              <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.414 10.5H9v-1.5z" />
              </svg>
              ✨ Refine & Proofread
            {/if}
          </button>
        </div>
        <textarea
          id="facultyQuestions"
          rows="4"
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
          placeholder="Any questions you have for students or topics to discuss at the next meeting..."
          bind:value={facultyQuestions}
          disabled={isSubmitting}
        ></textarea>
      </div>
      
      <!-- Meeting selection section for faculty -->
      <div>
        <label for="meeting-faculty" class="block text-sm font-medium text-gray-700 mb-2">
          Related Meeting <span class="text-red-500">*</span>
        </label>
        <select 
          id="meeting-faculty"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          bind:value={selectedMeeting}
          disabled={isSubmitting}
          required
        >
          <option value={null}>-- Select a meeting --</option>
          {#each meetings as meeting}
            <option value={meeting.id}>
              {meeting.title} - {formatDateTime(meeting.start_time)}
            </option>
          {/each}
        </select>
        <p class="mt-1 text-xs text-gray-500">
          Associate this update with an upcoming meeting
        </p>
      </div>

      <!-- Presentation checkbox for faculty -->
      <div class="flex items-center">
        <input
          type="checkbox"
          id="faculty-is-presenting"
          class="h-4 w-4 text-primary-700 focus:ring-primary-500 border-gray-300 rounded"
          bind:checked={facultyIsPresenting}
          disabled={isSubmitting}
        />
        <label for="faculty-is-presenting" class="ml-2 block text-sm font-medium text-gray-700">
          I will be presenting at this meeting
        </label>
      </div>
      
      <!-- File upload section for faculty -->
      <div>
        <label for="faculty-files" class="block text-sm font-medium text-gray-700 mb-2">
          Attach Files {facultyIsPresenting ? '(Required for presentations)' : '(Optional)'}
        </label>
        <input
          type="file"
          id="faculty-files"
          multiple
          accept="*/*"
          class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-primary-100 file:text-primary-700 hover:file:bg-primary-200"
          on:change={handleFacultyFileChange}
          disabled={isSubmitting}
          required={facultyIsPresenting}
        />
        <p class="mt-1 text-xs text-gray-500">
          {#if facultyIsPresenting}
            Please attach your presentation materials. Required for presentations.
          {:else}
            Upload any file type. Max 50MB per file, up to 20 files total.
          {/if}
        </p>
        
        <!-- Show selected files -->
        {#if facultyFiles && facultyFiles.length > 0}
          <div class="mt-3 p-3 bg-[rgb(var(--color-bg-secondary))] rounded-md">
            <h4 class="text-sm font-medium text-gray-700 mb-2">Selected Files ({facultyFiles.length}):</h4>
            <ul class="text-xs text-gray-600 space-y-1">
              {#each facultyFiles as file}
                <li class="flex justify-between">
                  <span class="truncate">{file.name}</span>
                  <span class="ml-2 text-gray-400">{formatFileSize(file.size)}</span>
                </li>
              {/each}
            </ul>
          </div>
        {/if}
      </div>
    {:else}
      <!-- STUDENT FORM -->
      
      <!-- Progress section -->
      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <label for="progress" class="block text-sm font-medium text-gray-700">
            Research Progress <span class="text-gray-400">(at least one section required *)</span>
          </label>
          <button 
            type="button"
            class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-sm font-medium rounded-lg shadow-sm hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            title="AI-powered text enhancement using domain-specific knowledge"
            on:click={(e) => refineText('progress', e)}
            disabled={isRefining || isSubmitting}
          >
            {#if isRefining && currentField === 'progress'}
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              AI Refining...
            {:else}
              <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.414 10.5H9v-1.5z" />
              </svg>
              ✨ Refine & Proofread
            {/if}
          </button>
        </div>
        <textarea
          id="progress"
          rows="5"
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
          placeholder="Describe your recent research progress, experiments performed, and results obtained..."
          bind:value={progressText}
          disabled={isSubmitting}
        ></textarea>
      </div>
      
      <!-- Challenges section -->
      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <label for="challenges" class="block text-sm font-medium text-gray-700">
            Challenges & Obstacles <span class="text-gray-400">(at least one section required *)</span>
          </label>
          <button 
            type="button"
            class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-sm font-medium rounded-lg shadow-sm hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            title="AI-powered text enhancement using domain-specific knowledge"
            on:click={(e) => refineText('challenges', e)}
            disabled={isRefining || isSubmitting}
          >
            {#if isRefining && currentField === 'challenges'}
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              AI Refining...
            {:else}
              <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.414 10.5H9v-1.5z" />
              </svg>
              ✨ Refine & Proofread
            {/if}
          </button>
        </div>
        <textarea
          id="challenges"
          rows="4"
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
          placeholder="Describe any challenges or obstacles you've encountered..."
          bind:value={challengesText}
          disabled={isSubmitting}
        ></textarea>
      </div>
      
      <!-- Goals section -->
      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <label for="goals" class="block text-sm font-medium text-gray-700">
            Upcoming Goals <span class="text-gray-400">(at least one section required *)</span>
          </label>
          <button 
            type="button"
            class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-sm font-medium rounded-lg shadow-sm hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            title="AI-powered text enhancement using domain-specific knowledge"
            on:click={(e) => refineText('goals', e)}
            disabled={isRefining || isSubmitting}
          >
            {#if isRefining && currentField === 'goals'}
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              AI Refining...
            {:else}
              <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.414 10.5H9v-1.5z" />
              </svg>
              ✨ Refine & Proofread
            {/if}
          </button>
        </div>
        <textarea
          id="goals"
          rows="4"
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
          placeholder="What are your research goals for the next two weeks..."
          bind:value={goalsText}
          disabled={isSubmitting}
        ></textarea>
      </div>
      
      <!-- Meeting notes section -->
      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <label for="meetingNotes" class="block text-sm font-medium text-gray-700">
            Meeting Notes
          </label>
          <button 
            type="button"
            class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-sm font-medium rounded-lg shadow-sm hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            title="AI-powered text enhancement using domain-specific knowledge"
            on:click={(e) => refineText('meetingNotes', e)}
            disabled={isRefining || isSubmitting}
          >
            {#if isRefining && currentField === 'meetingNotes'}
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              AI Refining...
            {:else}
              <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.414 10.5H9v-1.5z" />
              </svg>
              ✨ Refine & Proofread
            {/if}
          </button>
        </div>
        <textarea
          id="meetingNotes"
          rows="4"
          class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
          placeholder="Notes from your recent advisor/supervisor meetings..."
          bind:value={meetingNotes}
          disabled={isSubmitting}
        ></textarea>
      </div>
      
      <!-- Meeting selection section for students -->
      <div>
        <label for="meeting" class="block text-sm font-medium text-gray-700 mb-2">
          Related Meeting <span class="text-red-500">*</span>
        </label>
        <select 
          id="meeting"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          bind:value={selectedMeeting}
          disabled={isSubmitting}
          required
        >
          <option value={null}>-- Select a meeting --</option>
          {#each meetings as meeting}
            <option value={meeting.id}>
              {meeting.title} - {formatDateTime(meeting.start_time)}
            </option>
          {/each}
        </select>
        <p class="mt-1 text-xs text-gray-500">
          Associate this update with an upcoming meeting
        </p>
      </div>

      <!-- Presentation checkbox for students -->
      <div class="flex items-center">
        <input
          type="checkbox"
          id="is-presenting"
          class="h-4 w-4 text-primary-700 focus:ring-primary-500 border-gray-300 rounded"
          bind:checked={isPresenting}
          disabled={isSubmitting}
        />
        <label for="is-presenting" class="ml-2 block text-sm font-medium text-gray-700">
          I will be presenting at this meeting
        </label>
      </div>
      
      <!-- File upload section for students -->
      <div>
        <label for="files" class="block text-sm font-medium text-gray-700 mb-2">
          Attach Files {isPresenting ? '(Required for presentations)' : '(Optional)'}
        </label>
        <input
          type="file"
          id="files"
          multiple
          accept="*/*"
          class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-primary-100 file:text-primary-700 hover:file:bg-primary-200"
          on:change={handleFileChange}
          disabled={isSubmitting}
          required={isPresenting}
        />
        <p class="mt-1 text-xs text-gray-500">
          {#if isPresenting}
            Please attach your presentation materials. Required for presentations.
          {:else}
            Upload any file type. Max 50MB per file, up to 20 files total.
          {/if}
        </p>
        
        <!-- Show selected files -->
        {#if files && files.length > 0}
          <div class="mt-3 p-3 bg-[rgb(var(--color-bg-secondary))] rounded-md">
            <h4 class="text-sm font-medium text-gray-700 mb-2">Selected Files ({files.length}):</h4>
            <ul class="text-xs text-gray-600 space-y-1">
              {#each files as file}
                <li class="flex justify-between">
                  <span class="truncate">{file.name}</span>
                  <span class="ml-2 text-gray-400">{formatFileSize(file.size)}</span>
                </li>
              {/each}
            </ul>
          </div>
        {/if}
      </div>
    {/if}
    
    
    <!-- Optional Star Rating Feedback Section -->
    <div class="mt-6 p-3 bg-[rgb(var(--color-bg-secondary))] dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
      <h4 class="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">Help improve AI text refinement (optional)</h4>
      
      <div class="space-y-2">
        <!-- Text Quality Rating -->
        <div class="flex items-center justify-between">
          <span class="text-xs text-gray-600 dark:text-gray-400">Text quality improvement:</span>
          <div class="flex items-center space-x-1">
            {#each [1, 2, 3, 4, 5] as star}
              <button
                type="button"
                on:click={() => textQualityRating = star}
                on:mouseenter={() => textQualityHover = star}
                on:mouseleave={() => textQualityHover = 0}
                class="text-lg hover:scale-110 transition-transform duration-150 focus:outline-none"
              >
                <span class={
                  (textQualityHover > 0 ? star <= textQualityHover : star <= textQualityRating) 
                    ? 'text-yellow-400' 
                    : 'text-gray-300 dark:text-gray-600'
                }>★</span>
              </button>
            {/each}
          </div>
        </div>
        
        <!-- Helpfulness Rating -->
        <div class="flex items-center justify-between">
          <span class="text-xs text-gray-600 dark:text-gray-400">Overall helpfulness:</span>
          <div class="flex items-center space-x-1">
            {#each [1, 2, 3, 4, 5] as star}
              <button
                type="button"
                on:click={() => helpfulnessRating = star}
                on:mouseenter={() => helpfulnessHover = star}
                on:mouseleave={() => helpfulnessHover = 0}
                class="text-lg hover:scale-110 transition-transform duration-150 focus:outline-none"
              >
                <span class={
                  (helpfulnessHover > 0 ? star <= helpfulnessHover : star <= helpfulnessRating) 
                    ? 'text-yellow-400' 
                    : 'text-gray-300 dark:text-gray-600'
                }>★</span>
              </button>
            {/each}
          </div>
        </div>
        
        <!-- Ease of Use Rating -->
        <div class="flex items-center justify-between">
          <span class="text-xs text-gray-600 dark:text-gray-400">Ease of use:</span>
          <div class="flex items-center space-x-1">
            {#each [1, 2, 3, 4, 5] as star}
              <button
                type="button"
                on:click={() => easeOfUseRating = star}
                on:mouseenter={() => easeOfUseHover = star}
                on:mouseleave={() => easeOfUseHover = 0}
                class="text-lg hover:scale-110 transition-transform duration-150 focus:outline-none"
              >
                <span class={
                  (easeOfUseHover > 0 ? star <= easeOfUseHover : star <= easeOfUseRating) 
                    ? 'text-yellow-400' 
                    : 'text-gray-300 dark:text-gray-600'
                }>★</span>
              </button>
            {/each}
          </div>
        </div>
        
        <!-- Custom Feedback Text Box -->
        <div class="mt-3 pt-2 border-t border-gray-200 dark:border-gray-600">
          <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Additional feedback (optional)</label>
          <textarea 
            bind:value={customFeedbackText}
            rows="2"
            class="w-full text-xs border border-gray-300 rounded p-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            placeholder="What worked well? What could be improved? Any specific issues or suggestions?"
          ></textarea>
        </div>
        
        {#if textQualityRating > 0 || helpfulnessRating > 0 || easeOfUseRating > 0 || customFeedbackText.trim()}
          <p class="text-xs text-gray-500 dark:text-gray-400 italic mt-2">Thank you! This feedback will be submitted with your update.</p>
        {/if}
      </div>
    </div>

    <!-- Submit button -->
    <div class="flex justify-end">
      <button
        type="submit"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        disabled={isSubmitting}
      >
        {#if isSubmitting}
          <svg class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Submitting...
        {:else}
          {isEditMode ? 'Update Submission' : 'Submit Update'}
        {/if}
      </button>
    </div>
  </form>
  {/if}
</div>

<!-- Floating AI Refinement Widget -->
{#if refinementResult}
  <div 
    class="fixed z-50 w-96 p-4 bg-[rgb(var(--color-bg-primary))] dark:bg-gray-800 rounded-lg shadow-2xl border border-gray-200 dark:border-gray-600"
    style="left: {Math.max(10, Math.min(refinementPosition.x, window.innerWidth - 400))}px; top: {Math.max(10, Math.min(refinementPosition.y, window.innerHeight - 600))}px; max-width: calc(100vw - 20px); max-height: calc(100vh - 20px); overflow-y: auto;"
  >
    <!-- Hint for editing -->
    <div class="mb-3 p-2 bg-blue-50 dark:bg-blue-900/20 rounded border border-blue-200 dark:border-blue-800">
      <p class="text-xs text-blue-700 dark:text-blue-300 flex items-center">
        <svg class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        💡 Tip: You can edit the AI suggestions before applying them!
      </p>
    </div>
    
    <div class="flex justify-between items-start mb-3">
      <div class="flex items-center space-x-2">
        <svg class="h-4 w-4 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.414 10.5H9v-1.5z" />
        </svg>
        <div>
          <h3 class="text-sm font-semibold text-gray-800 dark:text-gray-200">AI Academic Assistant</h3>
          {#if refinementResult.word_count_original && refinementResult.word_count_refined}
            <p class="text-xs text-gray-500 dark:text-gray-400">
              {refinementResult.word_count_original} → {refinementResult.word_count_refined} words
              {#if refinementResult.word_count_refined !== refinementResult.word_count_original}
                <span class="text-blue-600 dark:text-blue-400">
                  ({refinementResult.word_count_refined > refinementResult.word_count_original ? '+' : ''}{refinementResult.word_count_refined - refinementResult.word_count_original})
                </span>
              {/if}
            </p>
          {/if}
        </div>
      </div>
      <button 
        type="button" 
        class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        on:click={() => refinementResult = null}
      >
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
    
    <!-- Refined text display/edit -->
    <div class="mb-3">
      <div class="flex justify-between items-center mb-1">
        <h4 class="text-xs font-medium text-gray-600 dark:text-gray-400">Refined Text:</h4>
        {#if !isEditingRefinement}
          <button 
            type="button"
            class="text-xs text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 flex items-center"
            on:click={startEditingRefinement}
          >
            <svg class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.414 10.5H9v-1.5z" />
            </svg>
            Edit
          </button>
        {/if}
      </div>
      
      {#if isEditingRefinement}
        <div class="space-y-2">
          <textarea
            bind:value={editedRefinedText}
            class="w-full text-sm text-gray-800 dark:text-gray-200 bg-[rgb(var(--color-bg-primary))] dark:bg-gray-700 p-3 rounded border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
            rows="4"
            placeholder="Edit the refined text..."
          ></textarea>
          <div class="flex justify-end space-x-2">
            <button
              type="button"
              class="px-3 py-1 text-xs bg-gray-200 hover:bg-gray-300 text-gray-700 rounded"
              on:click={cancelEditingRefinement}
            >
              Cancel
            </button>
            <button
              type="button"
              class="px-3 py-1 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded"
              on:click={saveEditedRefinement}
            >
              Save Changes
            </button>
          </div>
        </div>
      {:else}
        <div class="text-sm text-gray-800 dark:text-gray-200 bg-[rgb(var(--color-bg-secondary))] dark:bg-gray-700 p-3 rounded border text-wrap leading-relaxed">
          {refinementResult.refined_text || refinementResult.refined || 'No corrections needed'}
        </div>
      {/if}
    </div>
    
    <!-- Improvements Made Section -->
    {#if refinementResult.improvements_made && refinementResult.improvements_made.length > 0}
      <div class="mb-3">
        <h4 class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Improvements Made:</h4>
        <div class="bg-green-50 dark:bg-green-900/20 p-2 rounded border border-green-200 dark:border-green-800">
          <ul class="space-y-1">
            {#each refinementResult.improvements_made as improvement}
              <li class="flex items-start text-xs text-green-700 dark:text-green-300">
                <svg class="h-3 w-3 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                <span class="leading-relaxed">{improvement}</span>
              </li>
            {/each}
          </ul>
        </div>
      </div>
    {/if}

    <!-- Suggestions display -->
    {#if refinementResult.suggestions && refinementResult.suggestions.length > 0 && !refinementResult.suggestions.some(s => s.includes('Could not parse') || s.includes('Error processing'))}
      <div class="mb-3">
        <h4 class="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Writing Tips:</h4>
        <div class="bg-blue-50 dark:bg-blue-900/20 p-2 rounded border border-blue-200 dark:border-blue-800 max-h-32 overflow-y-auto">
          <ul class="space-y-1">
            {#each refinementResult.suggestions as suggestion}
              <li class="flex items-start text-xs text-blue-700 dark:text-blue-300">
                <span class="w-1 h-1 bg-blue-400 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                <span class="leading-relaxed">{suggestion}</span>
              </li>
            {/each}
          </ul>
        </div>
      </div>
    {/if}
    
    <!-- Action buttons -->
    <div class="flex gap-2">
      <button 
        type="button" 
        class="flex-1 inline-flex items-center justify-center px-3 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded transition-colors duration-200"
        on:click={applyRefinedText}
      >
        <svg class="h-4 w-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        Apply Enhanced Text
      </button>
      
      <!-- Feedback button -->
      <button 
        type="button" 
        class="px-3 py-2 text-sm font-medium text-white bg-orange-500 hover:bg-orange-600 rounded transition-colors duration-200 flex items-center"
        on:click={() => showFeedbackBox = true}
        title="Report an issue with this refinement"
      >
        <svg class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.959 8.959 0 01-2.73-.416L5 21l1.584-5.27A8.959 8.959 0 073 12a8 8 0 018-8 8 8 0 018 8z" />
        </svg>
        Feedback
      </button>
    </div>
  </div>
{/if}

<!-- Feedback Modal -->
{#if showFeedbackBox}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" on:click={() => showFeedbackBox = false}>
    <div class="bg-[rgb(var(--color-bg-primary))] dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4" on:click|stopPropagation>
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white">Refinement Feedback</h3>
        <button 
          on:click={() => showFeedbackBox = false}
          class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        >
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">How was this specific refinement?</label>
          <select bind:value={feedbackType} class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white">
            <option value="excellent">Excellent - Perfect improvement</option>
            <option value="good">Good - Helpful changes</option>
            <option value="improvement">Could be improved</option>
            <option value="error">Introduced errors</option>
            <option value="too_verbose">Too verbose/expanded</option>
            <option value="formatting">Wrong formatting</option>
            <option value="meaning_changed">Changed meaning</option>
            <option value="other">Other issue</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Details (optional)</label>
          <textarea 
            bind:value={feedbackText}
            rows="3"
            class="w-full border border-gray-300 rounded-md p-2 text-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            placeholder="Describe what went wrong or how it could be better..."
          ></textarea>
        </div>
        
        {#if feedbackSuccess}
          <div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md p-3">
            <p class="text-sm text-green-700 dark:text-green-400">✓ Feedback submitted successfully! This will help improve future refinements.</p>
          </div>
        {/if}
        
        <div class="flex gap-3 pt-2">
          <button 
            on:click={submitFeedback}
            disabled={isSubmittingFeedback}
            class="flex-1 inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {#if isSubmittingFeedback}
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Submitting...
            {:else}
              Submit Feedback
            {/if}
          </button>
          <button 
            on:click={() => showFeedbackBox = false}
            class="px-4 py-2 bg-gray-200 text-gray-800 text-sm font-medium rounded-md hover:bg-gray-300 dark:bg-gray-600 dark:text-gray-200 dark:hover:bg-[rgb(var(--color-bg-secondary))]0"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}