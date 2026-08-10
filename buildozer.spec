[app]

# (str) Title of your application
title = Inventory App

# (str) Package name
package.name = inventoryapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,xlsx,xls

# (str) Application versioning
version = 0.1

# (list) Application requirements
requirements = python3,kivy,openpyxl

# (str) Python version to use for python-for-android
p4a.python_version = 3.11

# (list) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = CAMERA, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 24

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Automatically accept SDK license agreements
android.accept_sdk_license = True

# (bool) Enable AndroidX support
android.enable_androidx = True

# (list) The Android archs to build for
android.archs = arm64-v8a

# (bool) enables Android auto backup feature
android.allow_backup = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
