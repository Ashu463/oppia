import os
import datetime
import requests

INACTIVE_DAYS = 7

def check_inactive_issues(github_token, repo_owner, repo_name):
    """
    Check for inactive issues in the given repository and unassign them if necessary.
    """
    headers = {"Authorization": f"token {github_token}"}
    repo_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
    
    # Fetch all open issues
    response = requests.get(repo_url, headers=headers, params={"state": "open"})
    response.raise_for_status()  # Raise an exception for HTTP errors
    issues = response.json()

    now = datetime.datetime.now(datetime.timezone.utc)

    for issue in issues:
        if not issue.get("assignee"):
            continue

        # Get timeline events for the issue
        events_url = issue["events_url"]
        events_response = requests.get(events_url, headers=headers)
        events_response.raise_for_status()
        events = events_response.json()

        # Get the last activity date
        last_activity_date = max(
            datetime.datetime.fromisoformat(event["created_at"].replace("Z", "+00:00"))
            for event in events
        )
        days_since_activity = (now - last_activity_date).total_seconds() / 86400

        if days_since_activity > INACTIVE_DAYS:
            # Unassign the issue
            unassign_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue['number']}/assignees"
            requests.delete(unassign_url, headers=headers, json={"assignees": [issue["assignee"]["login"]]})

            # Add a comment
            comment_url = issue["comments_url"]
            comment_body = {
                "body": f"@{issue['assignee']['login']} has been unassigned from this issue due to inactivity for more than {INACTIVE_DAYS} days. If you'd like to continue working on this issue, please request to be reassigned."
            }
            requests.post(comment_url, headers=headers, json=comment_body)

            print(f"Unassigned issue #{issue['number']} from {issue['assignee']['login']} due to inactivity")

if __name__ == "__main__":
    github_token = os.environ["GITHUB_TOKEN"]
    repo_owner = "oppia"
    repo_name = "oppia"

    check_inactive_issues(github_token, repo_owner, repo_name)
