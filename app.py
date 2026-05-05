import os
import subprocess
import requests

TOKEN = os.environ.get("GITHUB_TOKEN")
OWNER = "prashant2599"
REPO1 = "test1poc"
REPO2 = "test3poc"

def run(cmd):
    print(f"Running: {cmd}")
    return subprocess.check_output(cmd, shell=True).decode()

def lambda_handler(event, context):
    try:
        os.chdir("/tmp")

        # Cleanup
        run("rm -rf repo2")

        # ✅ Clone Repo2 (public - no token needed)
        run(f"git clone https://github.com/{OWNER}/{REPO2}.git")
        os.chdir(REPO2)

        # Create branch
        branch = "auto-sync"
        run(f"git checkout -b {branch}")

        # Add Repo1
        run(f"git remote add repo1 https://github.com/{OWNER}/{REPO1}.git")
        run("git fetch repo1")

        # Get latest commits (last 5)
        commits = run("git log repo1/main --pretty=format:%H -5").splitlines()

        print("Commits:", commits)

        # Cherry-pick
        for sha in commits:
            try:
                run(f"git cherry-pick {sha}")
            except subprocess.CalledProcessError:
                run("git cherry-pick --abort")
                return f"Conflict at {sha}"

        # ❗ Push needs auth
        run(f"git remote set-url origin https://{TOKEN}@github.com/{OWNER}/{REPO2}.git")
        run(f"git push origin {branch}")

        # Create PR
        response = requests.post(
            f"https://api.github.com/repos/{OWNER}/{REPO2}/pulls",
            headers={"Authorization": f"token {TOKEN}"},
            json={
                "title": "Auto Cherry Pick PR",
                "head": branch,
                "base": "main"
            }
        )

        print(response.text)

        return "✅ PR Created"

    except Exception as e:
        print("Error:", str(e))
        return "❌ Failed"