"""Wait for the requested SPA destination, including animated hash navigation."""
def goto_ready(page, url):
    response = page.goto(url)
    page.wait_for_function("document.querySelector('main')?.dataset.route === location.hash")
    return response
