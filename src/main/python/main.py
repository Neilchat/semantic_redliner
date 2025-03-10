from pathlib import Path

from fastapi import FastAPI, BackgroundTasks, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import markdown
from markdown_it import MarkdownIt

from config import config
from strategies.base.auto import AutoStrategy

app = FastAPI()

# In-memory store for results
results = {}
md = MarkdownIt()


def compare(company_name: str):
    strategy_key = "agenticCompare"


    results_folder = f"/Users/saswata/Documents/semantic_redliner/src/main/python/data/results/server/{strategy_key}_{company_name}"
    Path(results_folder).mkdir(parents=True, exist_ok=True)

    docpath1 = f"/Users/saswata/Documents/semantic_redliner/src/main/python/data/{company_name}_1.pdf"
    docpath2 = f"/Users/saswata/Documents/semantic_redliner/src/main/python/data/{company_name}_2.pdf"

    strategy = AutoStrategy.from_reference(strategy_key, config)
    result = strategy.compare_docs(
        docpath1,
        docpath2,
        results_folder
    )
    print(result)
    result_md = result.replace("```markdown", "").replace("```", "")

    results[company_name] = result_md

@app.get("/", response_class=HTMLResponse)
async def get_form():
    return """
    <html>
        <head><title>Company Report Generator</title></head>
        <body>
            <h1>Enter Company Name</h1>
            <form action="/submit" method="post">
                <input type="text" name="company" placeholder="Company Name" required>
                <input type="submit" value="Generate Report">
            </form>
        </body>
    </html>
    """


@app.post("/submit", response_class=HTMLResponse)
async def submit_company(company: str = Form(...), background_tasks: BackgroundTasks = None):
    # If not already computed, start background task
    if company not in results:
        background_tasks.add_task(compare, company)

    # Redirect to the processing page
    return RedirectResponse(url=f"/processing/{company}", status_code=303)


@app.get("/processing/{company}", response_class=HTMLResponse)
async def processing(company: str):
    if company in results:
        # Show the result
        return f"""
        <html>
            <head><title>Company Report</title></head>
            <body>
                <h1>Company Report for {company}</h1>
                <div class="tablePlated">{markdown.markdown(results[company], extensions=['markdown.extensions.tables'])}</div>
                <br><a href="/">Back</a>
            </body>
        </html>
        """

    # Still processing, show a loading message
    return f"""
    <html>
        <head>
            <title>Processing {company}</title>
            <meta http-equiv="refresh" content="5">
        </head>
        <body>
            <h1>Processing Report for {company}</h1>
            <p>Please wait... This may take a while.</p>
            <p>This page will refresh automatically.</p>
        </body>
    </html>
    """

