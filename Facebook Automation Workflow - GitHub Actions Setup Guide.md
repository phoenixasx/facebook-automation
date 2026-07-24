# Facebook Automation Workflow - GitHub Actions Setup Guide

## Overview

This guide walks you through deploying the corrected Facebook automation workflow to GitHub Actions. The new workflow properly handles Philippine timezone (PHT/UTC+8) scheduling and replicates your n8n automation logic.

## What Was Fixed

### The Problem
Your original GitHub Actions workflow was using **UTC cron times**, but your n8n workflow was designed to fire at **Philippine times (PHT)**. This 8-hour timezone mismatch caused the automation to run at unexpected times or not at all.

### The Solution
The new workflow:
- Uses correct **UTC cron times** that correspond to your intended **Philippine times**
- Includes `TZ: Asia/Manila` environment variable to ensure all timestamps are in PHT
- Replicates all n8n logic (persona selection, vibe assignment, news fetching, AI generation, image download, Facebook posting)
- Has proper error handling and logging
- Uses `actions/upload-artifact@v4` (no deprecation warnings)

## Timezone Conversion Reference

| Intended Time (PHT) | UTC Cron | Days |
|---|---|---|
| 8:00 PM | `0 12 * * 1-4` | Mon-Thu |
| 2:00 AM+1 | `0 18 * * 5` | Friday |
| 6:00 PM | `0 10 * * 6` | Saturday |
| 4:00 PM | `0 8 * * 0` | Sunday |

## Deployment Steps

### Step 1: Prepare Your Repository

1. Clone or open your repository locally
2. Create the following directory structure:
   ```
   .github/
   └── workflows/
       └── facebook-automation.yml
   ```

### Step 2: Add the Workflow File

1. Copy the contents of `facebook-automation-workflow.yml` to `.github/workflows/facebook-automation.yml`
2. Commit and push to your repository:
   ```bash
   git add .github/workflows/facebook-automation.yml
   git commit -m "Add corrected Facebook automation workflow with PHT timezone"
   git push
   ```

### Step 3: Add the Python Script

1. Copy `main_github_actions.py` to the root of your repository as `main.py`
2. Copy `requirements_github_actions.txt` to the root as `requirements.txt`
3. Commit and push:
   ```bash
   git add main.py requirements.txt
   git commit -m "Add Facebook automation Python script"
   git push
   ```

### Step 4: Configure GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** and add the following secrets:

| Secret Name | Value | Source |
|---|---|---|
| `GEMINI_API_KEY` | Your Google Gemini API key | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `FACEBOOK_ACCESS_TOKEN` | Your Facebook Page Access Token | [Facebook Developers](https://developers.facebook.com/) |
| `NEWSAPI_KEY` | Your NewsAPI key | [NewsAPI.org](https://newsapi.org/) |
| `GOOGLE_SHEETS_ID` | Your Google Sheets ID | From the URL: `https://docs.google.com/spreadsheets/d/{SHEETS_ID}/edit` |
| `POLLINATIONS_API_KEY` | Your Pollinations API key | [Pollinations](https://pollinations.ai/) |
| `FACEBOOK_PAGE_ID` | Your Facebook Page ID | From Facebook Page settings |

**How to add a secret:**
1. Click "New repository secret"
2. Enter the name (e.g., `GEMINI_API_KEY`)
3. Paste the value
4. Click "Add secret"

### Step 5: Test the Workflow

1. Go to your repository → **Actions** tab
2. Select **"Facebook Automation Post - PHT Schedule"** workflow
3. Click **"Run workflow"** → **"Run workflow"** to trigger it manually
4. Monitor the logs to ensure it runs successfully

## Troubleshooting

### Workflow Not Running at Scheduled Times

**Cause:** GitHub Actions requires at least one commit in the past 60 days for scheduled workflows to run.

**Fix:** Make a small commit to your repository to reactivate the schedule:
```bash
git commit --allow-empty -m "Reactivate scheduled workflows"
git push
```

### API Key Errors

**Cause:** Secrets not configured or incorrect values.

**Fix:** 
1. Double-check each secret in GitHub Settings
2. Verify API keys are still valid (not expired or revoked)
3. Check API quotas haven't been exceeded

### Facebook Post Not Appearing

**Cause:** Missing `FACEBOOK_PAGE_ID` or invalid access token.

**Fix:**
1. Verify the page ID is correct (numeric ID, not page name)
2. Ensure the access token has `pages_manage_posts` and `pages_read_engagement` permissions
3. Check the workflow logs for specific error messages

### Google Sheets Not Logging

**Cause:** Missing or invalid `GOOGLE_SHEETS_ID` or insufficient permissions.

**Fix:**
1. Verify the Sheets ID is correct
2. Ensure the service account has edit access to the spreadsheet
3. Check that the sheet has a "Sheet1" tab

### Image Generation Failing

**Cause:** Pollinations API quota exceeded or invalid API key.

**Fix:**
1. Check Pollinations dashboard for quota usage
2. Verify the API key is valid
3. The workflow will continue without an image if generation fails

## Monitoring and Logs

### View Workflow Runs

1. Go to your repository → **Actions** tab
2. Click on **"Facebook Automation Post - PHT Schedule"**
3. Click on a specific run to see detailed logs

### Download Logs

1. On the workflow run page, click **"Artifacts"**
2. Download `workflow-logs` (if the workflow failed)

### Manual Trigger

To test the workflow at any time:
1. Go to **Actions** tab
2. Select the workflow
3. Click **"Run workflow"** → **"Run workflow"**

## Customization

### Change Schedule Times

Edit `.github/workflows/facebook-automation.yml` and modify the `schedule` section:

```yaml
on:
  schedule:
    # Your custom cron times here
    - cron: '0 12 * * 1-4'  # Adjust these
```

Use [crontab.guru](https://crontab.guru/) to convert times, remembering to convert **from PHT to UTC** (subtract 8 hours).

### Modify Post Content

Edit `main.py` to customize:
- Persona definitions (lines 20-50)
- Day-specific themes and topics (lines 80-200)
- Gemini prompt template (lines 280-310)
- Image generation styles (lines 80-200)

### Add Additional Integrations

The script is modular and can be extended to:
- Post to Instagram (add Instagram API integration)
- Send Slack notifications
- Log to additional databases
- Generate multiple posts per run

## Support and Debugging

### Enable Debug Logging

Add this line to your workflow file to see more detailed logs:

```yaml
- name: Run Facebook automation
  env:
    DEBUG: 'true'
    # ... other env vars
  run: |
    python main.py
```

### Common Issues and Solutions

| Issue | Solution |
|---|---|
| Workflow not triggering | Make a commit to reactivate schedule; check GitHub Actions is enabled |
| API errors in logs | Verify all secrets are configured correctly |
| Posts not appearing | Check Facebook page ID and token permissions |
| Image not generating | Verify Pollinations API key and quota |
| Google Sheets not updating | Ensure service account has edit access to sheet |

## Next Steps

1. **Test the workflow** by running it manually
2. **Monitor the first few scheduled runs** to ensure everything works
3. **Adjust persona/vibe/topic logic** if needed
4. **Set up alerts** if the workflow fails (optional)

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Cron Expression Generator](https://crontab.guru/)
- [Google Gemini API Docs](https://ai.google.dev/docs)
- [Facebook Graph API Docs](https://developers.facebook.com/docs/graph-api)
- [NewsAPI Documentation](https://newsapi.org/docs)

---

**Questions?** Check the workflow logs for specific error messages, or review the Python script comments for implementation details.
