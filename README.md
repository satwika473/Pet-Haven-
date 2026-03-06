# Pet Haven - GitHub Pages Deployment

This repository is set up for GitHub Pages deployment as a **static site**.

## Created Entry Point
A root `index.html` file has been created based on `templates/landing_page.html`. This serves as the entry point for GitHub Pages.

## Limitations
Because GitHub Pages only hosts static files (HTML, CSS, JS), the following features **will not work**:
- **Database**: No user accounts, pets, or orders can be saved or retrieved.
- **Login/Registration**: These require a backend server.
- **Dynamic Content**: Pages will not update based on user actions.

## Next Steps to Fix Links
The `index.html` file links to other pages in the `templates/` folder. For those links to work correctly, you must update the links inside those HTML files as well:

1.  **Open** files in `templates/` (e.g., `templates/index.html`, `templates/apply.html`).
2.  **Update CSS/JS Links**: Change paths like `static/css/...` to `../static/css/...` (since the file is inside a subdirectory).
3.  **Update Navigation**: Change links like `{{ url_for('home') }}` to `../index.html`.

## Deployment
1.  Push this code to GitHub.
2.  Go to **Settings** > **Pages**.
3.  Select the **main** branch as the source.
4.  Your site will be live at `https://<your-username>.github.io/<repo-name>/`.
