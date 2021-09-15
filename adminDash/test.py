from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
print(BASE_DIR)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
print(STATIC_ROOT)
MEDIA_ROOT = os.path.join(BASE_DIR, 'static/images')
print(MEDIA_ROOT)