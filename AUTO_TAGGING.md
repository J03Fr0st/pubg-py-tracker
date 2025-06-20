# Auto-Tagging System

This project now includes an automatic tagging system that creates version tags whenever you push to the `main` branch.

## How It Works

1. **Automatic Patch Increment**: By default, every push to `main` will increment the patch version (e.g., `v1.0.0` → `v1.0.1`)

2. **Smart Version Bumping**: You can control the version bump by including specific keywords in your commit message:
   - `[major]` or `BREAKING CHANGE` → Major version bump (e.g., `v1.0.0` → `v2.0.0`)
   - `[minor]` or `feat:` → Minor version bump (e.g., `v1.0.0` → `v1.1.0`)
   - Default → Patch version bump (e.g., `v1.0.0` → `v1.0.1`)

3. **Skip Tagging**: Add `[skip-tag]` to your commit message to prevent automatic tag creation

## Examples

### Patch Release (Default)
```bash
git commit -m "Fix bug in Discord message formatting"
git push origin main
# Creates: v1.0.1 (if previous was v1.0.0)
```

### Minor Release
```bash
git commit -m "feat: Add new slash command for player stats"
git push origin main
# Creates: v1.1.0 (if previous was v1.0.x)
```

### Major Release
```bash
git commit -m "BREAKING CHANGE: Redesign API structure"
git push origin main
# Creates: v2.0.0 (if previous was v1.x.x)
```

### Skip Tagging
```bash
git commit -m "Update documentation [skip-tag]"
git push origin main
# No tag created
```

## What Happens After Tagging

1. **Automatic Release**: A GitHub release is created with the new tag
2. **Release Assets**: A `.tar.gz` deployment package is attached to the release
3. **Docker Build**: The Docker image is built (if configured)
4. **Release Notes**: Automatic release notes are generated

## First Time Setup

If this is your first time using the auto-tagging system and you don't have any existing tags:
- The system will start with `v0.0.1` for the first release
- If you want to start with a different version, create a tag manually first:

```bash
git tag v1.0.0
git push origin v1.0.0
```

## Monitoring

You can monitor the auto-tagging process in the GitHub Actions tab of your repository. Look for the "Python PUBG Tracker CI/CD" workflow runs.

## Troubleshooting

**No tag was created**: Check if your commit message contains `[skip-tag]` or if the workflow failed in the Actions tab.

**Wrong version number**: The system reads the latest git tag to determine the next version. Make sure your existing tags follow the `vX.Y.Z` format.

**Permission issues**: The workflow uses the `GITHUB_TOKEN` which should have sufficient permissions by default. If you encounter issues, check your repository's Actions permissions. 