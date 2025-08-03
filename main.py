from fastapi import FastAPI, Form, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil, os, subprocess

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def form():
    return """
    <h2>🚀 Deploy GBT App</h2>
    <form method="post" action="/deploy-form" enctype="multipart/form-data">
      <label>Repo (user/repo):</label><br>
      <input type="text" name="repo_url" /><br><br>
      <label>Domain:</label><br>
      <input type="text" name="domain" /><br><br>
      <label>Upload Logo:</label><br>
      <input type="file" name="logo" /><br><br>
      <input type="submit" value="Deploy" />
    </form>
    """

@app.post("/deploy-form")
async def deploy_form(
    repo_url: str = Form(...),
    domain: str = Form(...),
    logo: UploadFile = File(...)
):
    logo_path = f"/tmp/{logo.filename}"
    with open(logo_path, "wb") as f:
        shutil.copyfileobj(logo.file, f)
    return await deploy_post({
        "repo_url": repo_url,
        "domain": domain,
        "logo": logo_path
    })

@app.post("/deploy")
async def deploy_post(request: Request):
    data = await request.json() if isinstance(request, Request) else request
    repo = data.get("repo_url")
    domain = data.get("domain")
    logo = data.get("logo")

    if not all([repo, domain, logo]):
        return JSONResponse({"error": "Missing required fields"}, status_code=400)

    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        return JSONResponse({"error": "Missing GitHub token"}, status_code=500)

    clone_url = f"https://{github_token}:x-oauth-basic@github.com/{repo}.git"
    dest_path = "/tmp/repo"

    subprocess.run(f"rm -rf {dest_path}", shell=True)
    clone_result = subprocess.run(f"git clone {clone_url} {dest_path}", shell=True)

    if clone_result.returncode != 0:
        return JSONResponse({"error": "Failed to clone repo"}, status_code=500)

    return JSONResponse({
        "status": "Success",
        "cloned_repo": repo,
        "domain": domain,
        "logo_path": logo
    })
