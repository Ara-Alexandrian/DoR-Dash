# Avatar Soft Edge Fix Summary

## Issue Description
Users reported that avatars with soft edges (feathered edges) were losing their soft edge effect after upload. The avatars were being re-centered and the soft edges were converted to hard edges.

## Root Causes Identified

1. **Backend Alpha Channel Handling**: The backend was not properly preserving alpha channels when converting RGBA images to RGB for JPEG storage.

2. **Frontend Format Choice**: The frontend was always converting cropped avatars to JPEG format, which loses the alpha channel needed for soft edges.

## Changes Made

### Backend Changes (`backend/app/api/endpoints/users.py`)
- **Lines 370-390**: Improved alpha channel compositing when converting RGBA images to RGB
- Split RGBA channels explicitly and use proper alpha compositing
- Added specific handling for LA (grayscale + alpha) mode
- This preserves soft edge gradients when converting for JPEG storage

### Frontend Changes (`frontend/src/routes/profile/+page.svelte`)
- **Lines 484-506**: Modified blob creation to use PNG format when soft edges are applied
- Added logic to detect when feather radius > 0
- Uses PNG format to preserve alpha channel for soft edges
- Falls back to JPEG for hard-edged crops (smaller file size)

## Testing Instructions

### 1. Test Scripts Created
- `test_soft_edge_avatar.py` - Tests soft edge preservation
- `diagnose_avatar_issue.py` - Comprehensive diagnostic with positioning markers
- `test_frontend_avatar_crop.html` - Interactive frontend testing

### 2. Manual Testing Steps
1. Upload an avatar with soft edges enabled (feather radius > 0)
2. Check browser console for "format: PNG (soft edges)" message
3. Verify the uploaded avatar preserves soft edges
4. Test with different feather radius values
5. Test hard crop (feather radius = 0) still works with JPEG

### 3. Automated Testing
Run the diagnostic script:
```bash
python diagnose_avatar_issue.py
```

This will:
- Create a test avatar with markers and soft edges
- Upload it to the server
- Download and analyze the processed version
- Report whether soft edges and positioning were preserved

## Deployment Steps

1. **Backend Deployment**:
   ```bash
   cd backend
   # Restart the backend service to load the new code
   ```

2. **Frontend Deployment**:
   ```bash
   cd frontend
   npm run build
   # Restart the frontend service
   ```

3. **Verify Deployment**:
   - Check that both services restart successfully
   - Test avatar upload functionality
   - Monitor logs for any errors

## Expected Results

After these fixes:
1. Avatars with soft edges (feather radius > 0) will be uploaded as PNG
2. The backend will properly preserve alpha channels when processing
3. Soft edges will be maintained in the final stored image
4. User-positioned avatars will not be re-centered
5. The "processing" field in the API response will show "preserved" for 200x200 images

## Rollback Plan

If issues occur:
1. Revert the changes in both files
2. Restart both services
3. The previous behavior will be restored

## Future Improvements

Consider:
1. Adding server-side validation for PNG vs JPEG based on content
2. Implementing progressive JPEG for better quality/size tradeoff
3. Adding user preference for avatar format
4. Implementing WebP support for better compression with alpha channel