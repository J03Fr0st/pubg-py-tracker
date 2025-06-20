# 🚀 Release Guide

The GitHub Actions workflow now supports **two ways** to create releases:

## Method 1: Tag Push (Recommended)

Push a version tag to automatically create a GitHub release:

```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

**What happens:**
1. ✅ Runs tests and builds Docker image
2. ✅ Creates a GitHub release automatically
3. ✅ Generates release notes
4. ✅ Uploads deployment package

## Method 2: Manual GitHub Release

Create a release manually through GitHub UI:

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Choose a tag (or create new one like `v1.0.1`)
4. Fill in release title and description
5. Click "Publish release"

**What happens:**
1. ✅ Runs tests and builds Docker image
2. ✅ Uploads deployment package to the release

## Release Triggers

The workflow triggers on:
- ✅ **Tag pushes** matching `v*` pattern (v1.0.0, v2.1.3, etc.)
- ✅ **Manual releases** created through GitHub UI
- ✅ **Both** methods create downloadable `.tar.gz` packages

## Version Naming

Use semantic versioning for tags:
- `v1.0.0` - Major release
- `v1.1.0` - Minor release  
- `v1.0.1` - Patch release
- `v2.0.0-beta.1` - Pre-release

## What's Included in Releases

Each release includes:
- 📦 **Source code** (.tar.gz)
- 📋 **Installation instructions**
- 🐳 **Docker usage examples**
- 📝 **Automated release notes**

## Quick Release Commands

```bash
# Patch release (bug fixes)
git tag v1.0.1
git push origin v1.0.1

# Minor release (new features)  
git tag v1.1.0
git push origin v1.1.0

# Major release (breaking changes)
git tag v2.0.0
git push origin v2.0.0
```

## Troubleshooting

**Release not created?**
- ✅ Check tag format matches `v*` pattern
- ✅ Ensure you pushed the tag: `git push origin v1.0.0`
- ✅ Check GitHub Actions tab for build status

**Missing release assets?**
- ✅ Wait for workflow to complete (~3-5 minutes)
- ✅ Check if tests passed in Actions tab
- ✅ Verify `GITHUB_TOKEN` permissions (automatic)

The release stage is now **fixed and ready to use**! 🎉 