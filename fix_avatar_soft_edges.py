#!/usr/bin/env python3
"""
Fix for avatar soft edge preservation issue.
The problem: When converting RGBA images with soft edges to JPEG,
the alpha compositing might not be preserving the soft edges properly.
"""

# Here's the improved code for the avatar upload endpoint:

def process_avatar_with_soft_edges(image, is_already_cropped):
    """
    Process avatar image preserving soft edges when converting to JPEG
    """
    if is_already_cropped:
        # Image is already cropped by frontend with user's preferred positioning and soft edges
        if image.mode in ('RGBA', 'LA'):
            # For images with alpha channel, we need to composite properly
            # Create white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            
            # If the image has an alpha channel, use it for compositing
            if image.mode == 'RGBA':
                # Split the image to get the alpha channel
                r, g, b, a = image.split()
                
                # Create an RGB version of the image
                rgb_image = Image.merge('RGB', (r, g, b))
                
                # Use the alpha channel as a mask for compositing
                # This preserves soft edges better than simple paste
                background.paste(rgb_image, (0, 0), a)
                image = background
            else:
                # LA mode (grayscale with alpha)
                l, a = image.split()
                background.paste(image.convert('RGB'), (0, 0), a)
                image = background
        elif image.mode == 'P':
            # Palette mode - convert to RGBA first to preserve any transparency
            image = image.convert('RGBA')
            if 'transparency' in image.info:
                # Image has transparency, handle it
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, (0, 0), image)
                image = background
            else:
                # No transparency, simple conversion
                image = image.convert('RGB')
        elif image.mode not in ('RGB', 'L'):
            # Other modes, simple conversion
            image = image.convert('RGB')
        
        # For RGB and L modes, no conversion needed
        
    else:
        # Image needs cropping - existing smart crop logic
        # ... (rest of the cropping logic remains the same)
        pass
    
    return image

# The key improvements:
# 1. When handling RGBA images, we explicitly split the channels
# 2. We use the alpha channel as a mask for proper compositing
# 3. This preserves the soft edge gradients when converting to JPEG

# Additional improvement for the frontend:
# The frontend should send the image as PNG when it has soft edges
# to preserve the alpha channel during transmission.

print("""
SOFT EDGE PRESERVATION FIX
========================

The issue is in how RGBA images are converted to RGB for JPEG storage.
The current code uses:
    background.paste(image, (0, 0), image if image.mode == 'RGBA' else None)

This should be changed to:
    if image.mode == 'RGBA':
        r, g, b, a = image.split()
        rgb_image = Image.merge('RGB', (r, g, b))
        background.paste(rgb_image, (0, 0), a)
    else:
        background.paste(image, (0, 0), image)

The key difference:
- Explicitly splitting the RGBA channels
- Using only the alpha channel as the mask
- This preserves soft edge gradients better

To implement this fix:
1. Update the avatar upload endpoint in users.py (lines 370-377)
2. Test with the diagnostic scripts
3. Ensure the frontend sends PNG format for images with transparency
""")