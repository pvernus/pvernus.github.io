# /publish — Commit and deploy the website

Commit all current changes and push to GitHub, triggering the GitHub Actions deployment.

## Input
$ARGUMENTS

## Instructions

1. Use the input as the commit message. If no input is given, use `"Update site"`.

2. Run the following three commands in sequence, stopping if any fails:
   - `git add .`
   - `git commit -m "<message>"`
   - `git push origin main`

3. Report the result:
   - On success: confirm the push succeeded and remind the user the site will be live at https://pvernus.github.io in ~2 minutes.
   - On failure: show the error and suggest a fix.
