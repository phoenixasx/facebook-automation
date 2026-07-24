# Validation Checklist for Facebook Automation Workflow

## Pre-Deployment Validation

### Code Quality
- [x] Python script follows PEP 8 conventions
- [x] All API integrations properly error-handled
- [x] Logging configured for debugging
- [x] No hardcoded secrets in code
- [x] Requirements.txt includes all dependencies
- [x] GitHub Actions workflow uses v4 of actions (no deprecation warnings)

### Timezone Accuracy
- [x] Cron times correctly converted from PHT to UTC
  - PHT 8:00 PM = UTC 12:00 PM ✓
  - PHT 2:00 AM+1 = UTC 6:00 PM ✓
  - PHT 6:00 PM = UTC 10:00 AM ✓
  - PHT 4:00 PM = UTC 8:00 AM ✓
- [x] `TZ: Asia/Manila` environment variable set
- [x] All timestamps logged in PHT

### API Integration Coverage
- [x] Gemini API (post generation)
- [x] NewsAPI (trending news)
- [x] Pollinations API (image generation)
- [x] Facebook Graph API (posting)
- [x] Google Sheets API (logging)

### Feature Parity with n8n
- [x] Persona selection (3 personas cycling weekly)
- [x] Vibe assignment (3 vibes with weighted distribution)
- [x] Day-specific themes and topics (7 day configs)
- [x] News fetching from Philippines
- [x] AI post generation with context
- [x] Image generation and download
- [x] Facebook posting with image
- [x] First comment posting
- [x] Google Sheets logging

## Deployment Checklist

### Repository Setup
- [ ] `.github/workflows/facebook-automation.yml` created
- [ ] `main.py` added to repository root
- [ ] `requirements.txt` added to repository root
- [ ] All files committed and pushed to GitHub
- [ ] GitHub Actions enabled in repository settings

### Secrets Configuration
- [ ] `GEMINI_API_KEY` added to GitHub Secrets
- [ ] `FACEBOOK_ACCESS_TOKEN` added to GitHub Secrets
- [ ] `NEWSAPI_KEY` added to GitHub Secrets
- [ ] `GOOGLE_SHEETS_ID` added to GitHub Secrets
- [ ] `POLLINATIONS_API_KEY` added to GitHub Secrets
- [ ] `FACEBOOK_PAGE_ID` added to GitHub Secrets

### API Verification
- [ ] Gemini API key is valid and has quota
- [ ] Facebook token has `pages_manage_posts` permission
- [ ] NewsAPI key is active
- [ ] Pollinations API key is valid
- [ ] Google Sheets ID is correct and accessible
- [ ] Facebook Page ID is numeric (not page name)

## Testing Checklist

### Manual Test Run
1. [ ] Go to GitHub Actions tab
2. [ ] Select "Facebook Automation Post - PHT Schedule"
3. [ ] Click "Run workflow" → "Run workflow"
4. [ ] Wait for completion (should take 2-5 minutes)
5. [ ] Check logs for any errors
6. [ ] Verify post appeared on Facebook page
7. [ ] Check Google Sheets for logged entry
8. [ ] Verify image was generated and posted

### Scheduled Run Verification
- [ ] Wait for first scheduled run (check cron times)
- [ ] Verify post appears at expected time
- [ ] Check workflow logs for successful execution
- [ ] Monitor for 2-3 scheduled runs to ensure consistency

### Error Scenarios
- [ ] Test with invalid API key (should fail gracefully)
- [ ] Test with missing Facebook Page ID (should skip posting)
- [ ] Test with invalid Google Sheets ID (should log warning)
- [ ] Verify logs are uploaded on failure

## Post-Deployment Monitoring

### Daily Checks (First Week)
- [ ] Workflow runs at scheduled times
- [ ] Posts appear on Facebook within 5 minutes of scheduled time
- [ ] Images are generated and posted correctly
- [ ] Google Sheets logging is working
- [ ] No error messages in workflow logs

### Weekly Checks
- [ ] All 4 scheduled times are executing
- [ ] Persona rotation is working (changes weekly)
- [ ] Vibe selection is varied
- [ ] News integration is pulling current articles
- [ ] Post quality meets expectations

### Monthly Checks
- [ ] No accumulated errors or warnings
- [ ] API quotas are within acceptable usage
- [ ] Facebook engagement metrics are tracked
- [ ] Consider adjusting topics or personas based on performance

## Rollback Plan

If issues arise, follow these steps:

1. **Disable the workflow** (temporary)
   - Go to `.github/workflows/facebook-automation.yml`
   - Add `enabled: false` to the workflow
   - Commit and push

2. **Investigate the issue**
   - Check workflow logs for specific error
   - Verify all secrets are still valid
   - Test API endpoints manually

3. **Fix and re-enable**
   - Update the workflow or Python script
   - Commit and push
   - Re-enable the workflow
   - Run a manual test

## Success Criteria

The workflow is considered successful when:

✓ **Scheduling:** Posts run at the exact scheduled times (within 5 minutes)
✓ **Reliability:** 95%+ of scheduled runs complete successfully
✓ **Quality:** Generated posts are relevant and engaging
✓ **Logging:** All posts are logged to Google Sheets with metadata
✓ **Errors:** Any failures are logged and don't crash the workflow
✓ **Performance:** Workflow completes in under 5 minutes per run

## Quick Troubleshooting

| Symptom | Likely Cause | Quick Fix |
|---|---|---|
| Workflow not running at all | Schedule disabled or no recent commit | Make a commit to reactivate |
| "API key invalid" error | Secret not configured or expired | Verify secret in GitHub Settings |
| Post not appearing on Facebook | Missing Page ID or invalid token | Check FACEBOOK_PAGE_ID and token permissions |
| Image not generating | Pollinations quota exceeded | Check Pollinations dashboard |
| Google Sheets not logging | Invalid Sheets ID or permissions | Verify Sheets ID and service account access |
| Workflow timeout | Script taking too long | Check for API rate limiting or network issues |

## Contact & Support

For issues:
1. Check the workflow logs first (most detailed information)
2. Review this checklist for common issues
3. Consult the DEPLOYMENT_GUIDE.md for detailed setup
4. Check individual API documentation for service-specific errors

---

**Last Updated:** July 2026
**Workflow Version:** 1.0
**Status:** Ready for Deployment
