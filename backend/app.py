from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = FastAPI()


# -----------------------------
# CORS
# -----------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

groq_client = Groq(api_key=GROQ_API_KEY)


# -----------------------------
# HOME
# -----------------------------

@app.get("/")
def home():
    return {
        "message": "GitHub Therapist is alive 🧠"
    }


# -----------------------------
# GITHUB USER
# -----------------------------

@app.get("/github/{username}")
async def get_github_user(username: str):

    url = f"https://api.github.com/users/{username}"

    async with httpx.AsyncClient() as client:

        response = await client.get(
            url,
            headers=HEADERS
        )

    return response.json()


# -----------------------------
# README CHECK
# -----------------------------

async def check_readme(client, username, repo_name):

    url = (
        f"https://api.github.com/repos/"
        f"{username}/{repo_name}/readme"
    )

    response = await client.get(
        url,
        headers=HEADERS
    )

    return response.status_code == 200


# -----------------------------
# TEST CHECK
# -----------------------------

async def check_tests(client, username, repo_name):

    url = (
        f"https://api.github.com/repos/"
        f"{username}/{repo_name}/contents"
    )

    response = await client.get(
        url,
        headers=HEADERS
    )

    if response.status_code != 200:
        return False

    files = response.json()

    for item in files:

        name = item["name"].lower()

        if (
            name in ["tests", "test"]
            or name.startswith("test_")
        ):
            return True

    return False


# -----------------------------
# PROJECT SCORE
# -----------------------------

def calculate_project_score(
    repo,
    has_readme,
    has_tests
):

    score = 0

    if has_readme:
        score += 30

    if repo["description"]:
        score += 15

    if repo["language"]:
        score += 15

    if has_tests:
        score += 25

    if repo["stargazers_count"] > 0:
        score += 5

    if repo["forks_count"] > 0:
        score += 5

    if repo["size"] > 0:
        score += 5

    return score


# -----------------------------
# DEVELOPER REPORT
# -----------------------------

def generate_report(
    repos,
    readme_count,
    tests_count,
    health_score
):

    total = len(repos)

    strengths = []
    weaknesses = []
    prescription = []

    if total == 0:

        return {
            "diagnosis": "No Public Projects Found",
            "strengths": [],
            "weaknesses": [
                "No public repositories were found"
            ],
            "prescription": [
                "Build and publish at least one meaningful project"
            ],
            "recruiter_readiness": 0
        }

    # README

    if readme_count >= total * 0.7:

        strengths.append(
            "Good documentation coverage"
        )

    else:

        weaknesses.append(
            "Many projects are missing README files"
        )

        prescription.append(
            "Add proper README files to your strongest projects"
        )

    # TESTS

    if tests_count >= total * 0.5:

        strengths.append(
            "Good testing habits"
        )

    else:

        weaknesses.append(
            "Testing coverage is weak"
        )

        prescription.append(
            "Add meaningful tests to your best project"
        )

    # PROJECT QUALITY

    quality_projects = 0

    for repo in repos:

        if repo["project_score"] >= 70:
            quality_projects += 1

    if quality_projects >= max(1, total // 2):

        strengths.append(
            "Several projects show good engineering quality"
        )

    else:

        weaknesses.append(
            "Many projects need stronger engineering signals"
        )

        prescription.append(
            "Polish fewer projects instead of creating many new ones"
        )

    # HEALTH

    if health_score >= 80:

        diagnosis = "Healthy Developer Profile"

    elif health_score >= 60:

        diagnosis = "Good Potential, Needs Polish"

    elif health_score >= 40:

        diagnosis = "GitHub Needs Therapy"

    else:

        diagnosis = "Severe Project Neglect"

    # RECRUITER READINESS

    recruiter_readiness = health_score

    if readme_count == 0:
        recruiter_readiness -= 10

    if tests_count == 0:
        recruiter_readiness -= 10

    recruiter_readiness = max(
        0,
        min(100, recruiter_readiness)
    )

    if not prescription:

        prescription.append(
            "Keep your strongest projects polished "
            "and focus on production-level features"
        )

    return {
        "diagnosis": diagnosis,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "prescription": prescription,
        "recruiter_readiness": recruiter_readiness
    }


# -----------------------------
# GITHUB ANALYSIS
# -----------------------------

@app.get("/github/{username}/repos")
async def get_github_repos(username: str):

    url = (
        f"https://api.github.com/users/"
        f"{username}/repos"
    )

    async with httpx.AsyncClient() as client:

        response = await client.get(
            url,
            headers=HEADERS
        )

        if response.status_code != 200:

            return {
                "error": "GitHub API request failed",
                "status_code": response.status_code,
                "details": response.json()
            }

        repos = response.json()

        analyzed_repos = []

        readme_count = 0
        tests_count = 0
        total_score = 0

        for repo in repos:

            has_readme = await check_readme(
                client,
                username,
                repo["name"]
            )

            has_tests = await check_tests(
                client,
                username,
                repo["name"]
            )

            if has_readme:
                readme_count += 1

            if has_tests:
                tests_count += 1

            project_score = calculate_project_score(
                repo,
                has_readme,
                has_tests
            )

            total_score += project_score

            analyzed_repos.append({

                "name": repo["name"],

                "description": repo["description"],

                "language": repo["language"],

                "stars": repo["stargazers_count"],

                "forks": repo["forks_count"],

                "has_readme": has_readme,

                "has_tests": has_tests,

                "project_score": project_score

            })

        total_repositories = len(repos)

        if total_repositories > 0:

            developer_health = round(
                total_score / total_repositories
            )

        else:

            developer_health = 0

        report = generate_report(
            analyzed_repos,
            readme_count,
            tests_count,
            developer_health
        )

    return {

        "username": username,

        "developer_health": developer_health,

        "total_repositories": total_repositories,

        "repositories_with_readme": readme_count,

        "repositories_with_tests": tests_count,

        "average_project_score": developer_health,

        "diagnosis": report["diagnosis"],

        "recruiter_readiness": report[
            "recruiter_readiness"
        ],

        "strengths": report["strengths"],

        "weaknesses": report["weaknesses"],

        "prescription": report["prescription"],

        "projects": analyzed_repos

    }


# ==================================================
# AI THERAPIST
# ==================================================

@app.get("/github/{username}/ai-report")
async def ai_report(
    username: str,
    mode: str = "therapist"
):

    # First get GitHub analysis
    analysis = await get_github_repos(username)

    # Stop if GitHub analysis failed
    if "error" in analysis:

        return analysis

    # Valid modes
    valid_modes = [
        "therapist",
        "roast",
        "recruiter"
    ]

    if mode not in valid_modes:

        mode = "therapist"

    # -----------------------------
    # Mode instructions
    # -----------------------------

    if mode == "therapist":

        style = """
You are a funny but helpful GitHub therapist.

Talk to the developer like a supportive friend.

Be slightly Gen-Z and humorous.

Do NOT be cruel.

Explain what is good, what is bad,
and exactly what they should improve.
"""

    elif mode == "roast":

        style = """
You are a brutally funny GitHub roast therapist.

Roast the developer's GitHub based ONLY
on the provided data.

Be funny and Gen-Z.

Do not make personal attacks.

After the roast, give useful fixes.
"""

    else:

        style = """
You are a startup technical recruiter.

Evaluate this GitHub profile professionally.

Focus on engineering signals,
project quality, documentation,
testing and recruiter readiness.

Give honest but constructive feedback.
"""


    # -----------------------------
    # Prompt
    # -----------------------------

    prompt = f"""
{style}

Developer username:
{username}

Developer Health:
{analysis["developer_health"]}/100

Recruiter Readiness:
{analysis["recruiter_readiness"]}/100

Diagnosis:
{analysis["diagnosis"]}

Strengths:
{analysis["strengths"]}

Weaknesses:
{analysis["weaknesses"]}

Prescription:
{analysis["prescription"]}

Projects:
{analysis["projects"]}

Give the developer:

1. A short opening reaction.
2. What they are doing well.
3. What is hurting their profile.
4. The top 3 actions they should take next.
5. A short final verdict.

Keep the response concise and practical.
"""


    # -----------------------------
    # Call Groq
    # -----------------------------

    try:

        completion = groq_client.chat.completions.create(

           model="openai/gpt-oss-20b",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.7,

            max_tokens=700
        )

        ai_message = completion.choices[
            0
        ].message.content


    except Exception as e:

        return {

            "error": "AI request failed",

            "details": str(e),

            "github_analysis": analysis

        }


    # -----------------------------
    # Final response
    # -----------------------------

    return {

        "username": username,

        "mode": mode,

        "developer_health":
            analysis["developer_health"],

        "recruiter_readiness":
            analysis["recruiter_readiness"],

        "diagnosis":
            analysis["diagnosis"],

        "ai_message":
            ai_message,

        "github_analysis":
            analysis

    }