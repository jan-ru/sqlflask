
# TIL
## 2025-05-05

I'll write the TIL here and later move it to the correct file.

First I learned about static sites (using quarto) and found a convenient way to deploy them on GitHub Pages.

Next came the requirement to have at least some dynamic content so I experimented with pyodide. I am impressed for example with jupyterlite and marimbo.

Trying to stay away from full fledged frontend frameworks like react/vue, I am trying to do some frontend work with just HTML and htmx and (tabulator javascript lib).

Anyway, it soon becomes apparant that certain use cases require persistence. Hence I am now trying to work with sqlite3. Second, I did a prototype with Python.

Both the Deno and Python prototypes have been deployed to Railway (via GitHub). Neither is finished but both are running ok. (Albeit the flask version directly on gunicorn. Caddy needs to be put in front of it as a reverse proxy.)

The current idea is to pause doing a third (FastAPI) prototype. Instead I will look to improve SQLFlask to try and do some production work with it (either grading or excel).
