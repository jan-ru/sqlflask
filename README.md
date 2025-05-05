I'll write the TIL here and later move it to the correct file.
# TIL
## 2023-10-04

First I learned about static sites (using quarto) and found a convenient way to deploy them on GitHub Pages.

Next came the requirement to have at least some dynamic content so I experimented with pyodide. I am impressed for example with jupyterlite and marimbo.

Trying to stay away from full fledged frontend frameworks like react/vue, I am trying to do some frontend work with just HTML and htmx.

Anyway, it soon becomes apparant that certain use cases require persistence. Hence I am now trying to work with sqlite3. First I did a prototype using Deno. Deno use a sqlite on wasm which is great for testing and/or read-only databases but it doesn't provide for persistance as the database can not be written to disk. Second, I did a prototype with Python. This is way easier, partly because I know Python and I don't know Typescript but also, for example, because sqlite3 is built into Python.

Both the Deno and Python prototypes have been deployed to Railway (via GitHub). Neither is finished but both are running ok. (Albeit the flask version still on the development server, to be update to a production WSGI server later.)

The current idea is to pause doing a third (FastAPI) prototype. Instead I will look to improve SQLFlask to try and do some production work with it (either grading or excell).