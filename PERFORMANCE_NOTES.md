# Performance Considerations

## Image Generation Performance Issue

### Current State
The application currently performs synchronous image generation during web requests in two places:

1. **Subject Creation** (`app/main/routes.py` lines 114-125): When adding a new subject, the route generates a static icon image synchronously
2. **Task Display** (`app/main/routes.py` lines 74-76): When displaying the home page, dynamic image URLs are generated for each task

### Impact
- **Subject Creation**: Can cause request timeouts if the Pollinations API is slow
- **Task Display**: Limited impact since only URL generation (no HTTP requests)

### Recommended Solutions

#### Option 1: Background Task Queue (Preferred)
```python
# Using Celery or similar task queue
@celery.task
def generate_subject_image(subject_name, file_path):
    with PollinationsImage() as img_client:
        img_client(
            prompt=f"school subject {subject_name} icon",
            save=True,
            file=file_path,
            width=256,
            height=256,
        )

# In route:
if current_app.content_library.add_subject(subject):
    # Queue image generation
    generate_subject_image.delay(subject, path)
    flash(f"Fach '{subject}' hinzugefügt. Bild wird generiert...", "success")
```

#### Option 2: Placeholder Images
```python
# Generate a placeholder image immediately, replace later
def create_placeholder_image(subject_name, file_path):
    # Create simple text-based placeholder
    pass

# Queue actual image generation for later
```

#### Option 3: Client-Side Loading
```javascript
// Load images asynchronously on the client side
fetch(`/api/generate-image/${subject}`)
    .then(response => response.blob())
    .then(blob => {
        // Update UI with generated image
    });
```

### Implementation Priority
This is a **medium priority** issue that should be addressed when:
1. User reports indicate slow response times
2. The application scales to handle more concurrent users
3. Integration with slower external APIs becomes problematic

The current implementation works well for development and low-traffic scenarios.