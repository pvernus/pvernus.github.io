# /publish — Commit and deploy the website

Commit the changes described by the message and push to GitHub, triggering the
GitHub Actions deployment.

## Input
$ARGUMENTS

## Instructions

1. **Determine the commit message.** Use the input as-is. If no input is given, use
   `"Update site"`.

2. **Inspect the working tree** with `git status --short`. Do not stage anything yet.

3. **Decide the scope.**

   - **Input describes a specific change** (e.g. "Add two shows to watch list") →
     scope is only the files that belong to that change. A file belongs if you
     edited it this session for that purpose, or its path clearly matches the
     described change.
   - **No input given, or the message is generic** ("Update site") → everything in
     the working tree is in scope.

   When a file's relevance is uncertain, treat it as out of scope. Leaving a file
   for the next commit costs nothing; publishing an unfinished note to a live site
   cannot be undone without rewriting history.

4. **Stage explicitly by path** — `git add <path> [<path>…]`, one path per file in
   scope. Never use `git add .` or `git add -A` when the scope is narrower than the
   whole tree.

5. **Before committing, if anything is being left behind**, list the out-of-scope
   files and state plainly that they will not be included. If the scope turns out to
   be empty (nothing in the tree matches the message), stop and report that instead
   of committing.

6. **Commit and push**, stopping if either fails:
   - `git commit -m "<message>"`
   - `git push origin main`

7. **Report the result:**
   - On success: list the files actually committed, repeat the files left
     uncommitted, and note the site will be live at https://pvernus.github.io in
     ~2 minutes.
   - On failure: show the error and suggest a fix.

## Note

Untracked garden notes and auto-generated `garden/sources/*.qmd` files accumulate in
the working tree between sessions. They are a normal steady state, not a sign that
something needs committing — only include them when the message is about them.
