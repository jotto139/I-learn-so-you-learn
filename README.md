# Study Notes

A Markdown-based course notebook, prepared for GitHub Pages.

## Add a note

1. Copy `templates/topic.md` into `courses/principles-of-neuroscience/`.
2. Name it something like `02-your-topic.md`. Filenames determine the order; use lowercase letters, numbers, and hyphens.
3. Edit the title, description, and status at the top. Write your explanation below the second `---`.
4. Upload your changes to the `main` branch on GitHub. Once Pages is configured, the site rebuilds automatically.

Each note becomes its own page and is listed automatically. Headings become a table of contents. The starter note is a writing scaffold, not a summary of the textbook.

## Formatting

Use `## Heading`, `**bold**`, `*italics*`, numbered lists, Markdown tables, and `> blockquotes`. Use `$x^2$` for inline math and `$$ ... $$` for display math. Math rendering needs an internet connection.

Put pictures in the course's `images` folder and reference them with `![Description](images/filename.png)`. Link to another note with `[Topic](02-your-topic.html)`. Browser print produces a clean reading copy.

Word documents can be provided as source material or formatting references; they are not imported automatically. The Markdown files are the maintained website content. Only put content intended for public viewing in course folders.

## Add a course

Create another folder under `courses`, copy `course.json` from the existing course, and edit its title, description, and label. Add Markdown notes there. The homepage discovers courses automatically.

## Preview locally

Requires Python 3.11 or later:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python build.py
.venv\Scripts\python -m http.server 8000 --directory dist
```

Open http://localhost:8000. Run the build command and refresh after editing notes.

## Publish on GitHub Pages

1. Create a public GitHub repository named `notes`.
2. Upload this project's source, including `.github/workflows/pages.yml`, to its `main` branch. Do not upload `.venv` or `dist`.
3. In the repository, open **Settings → Pages → Build and deployment → Source**, and choose **GitHub Actions**.
4. In **Actions**, run **Publish notes** if the initial run happened before Pages was enabled.
5. Once deployment succeeds, Pages shows your live address, usually `https://YOUR-USERNAME.github.io/notes/`.

The workflow builds and publishes every subsequent update to `main`. All links use relative paths, so the site also works under a repository subpath or a custom domain.
