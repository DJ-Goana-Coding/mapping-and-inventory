#!/usr/bin/env python3
"""
CITADEL ARCHITECT - WORKFLOW DEPLOYMENT ENGINE
Deploys sync workflows to all discovered DJ-Goana-Coding repositories

Authority: Citadel Architect v25.0.OMNI+
"""
import os
import sys
import json
import base64
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional


GITHUB_ORG = "DJ-Goana-Coding"
GITHUB_API = "https://api.github.com"


def load_repo_registry() -> Dict[str, Any]:
    """Load the repository bridge registry."""
    registry_path = "repo_bridge_registry.json"
    
    if not os.path.exists(registry_path):
        print("❌ Registry not found. Run discover_all_repos.py first!")
        sys.exit(1)
    
    with open(registry_path, "r") as f:
        return json.load(f)


def read_workflow_template(template_name: str) -> str:
    """Read a workflow template file."""
    template_path = f".github/workflow-templates/{template_name}"
    
    if not os.path.exists(template_path):
        print(f"❌ Template not found: {template_path}")
        sys.exit(1)
    
    with open(template_path, "r") as f:
        return f.read()


def check_workflow_exists(owner: str, repo: str, workflow_name: str, token: str) -> bool:
    """Check if a workflow file already exists in a repository."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/.github/workflows/{workflow_name}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    return response.status_code == 200


def create_or_update_workflow(
    owner: str,
    repo: str,
    workflow_name: str,
    content: str,
    token: str,
    force: bool = False
) -> bool:
    """
    Create or update a workflow file in a repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        workflow_name: Name of the workflow file
        content: Workflow file content
        token: GitHub token
        force: Whether to force update existing workflows
        
    Returns:
        True if successful, False otherwise
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/.github/workflows/{workflow_name}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }
    
    # Check if file exists
    existing_sha = None
    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code == 200:
        existing_sha = response.json()["sha"]
        
        if not force:
            print(f"    ⊙  Workflow already exists (use --force to update)")
            return True
    
    # Encode content
    content_bytes = content.encode("utf-8")
    content_b64 = base64.b64encode(content_bytes).decode("utf-8")
    
    # Prepare payload
    payload = {
        "message": f"🏛️ Citadel Architect: Deploy {workflow_name}\n\nAuthority: v25.0.OMNI+\nDeployed: {datetime.utcnow().isoformat()}Z",
        "content": content_b64,
        "branch": "main"
    }
    
    if existing_sha:
        payload["sha"] = existing_sha
    
    # Create or update
    response = requests.put(url, headers=headers, json=payload, timeout=30)
    
    if response.status_code in [200, 201]:
        action = "Updated" if existing_sha else "Created"
        print(f"    ✅ {action} {workflow_name}")
        return True
    else:
        print(f"    ❌ Failed: {response.status_code} - {response.text[:100]}")
        return False


def deploy_to_repository(
    repo_info: Dict[str, Any],
    token: str,
    workflows: List[str],
    force: bool = False,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Deploy workflows to a single repository.
    
    Args:
        repo_info: Repository information from registry
        token: GitHub token
        workflows: List of workflow names to deploy
        force: Whether to force update existing workflows
        dry_run: Whether to simulate without actual deployment
        
    Returns:
        Deployment result dictionary
    """
    repo_name = repo_info["name"]
    
    print(f"\n📦 {repo_name}")
    
    # Skip archived repos
    if repo_info.get("is_archived", False):
        print("    ⊘  Skipping (archived)")
        return {"repo": repo_name, "status": "skipped", "reason": "archived"}
    
    # Skip mapping-and-inventory itself
    if repo_name == "mapping-and-inventory":
        print("    ⊘  Skipping (this is the hub)")
        return {"repo": repo_name, "status": "skipped", "reason": "is_hub"}
    
    if dry_run:
        print("    🔍 DRY RUN - would deploy workflows")
        return {"repo": repo_name, "status": "dry_run"}
    
    results = {"repo": repo_name, "workflows": {}}
    
    for workflow_file in workflows:
        workflow_content = read_workflow_template(workflow_file)
        
        success = create_or_update_workflow(
            GITHUB_ORG,
            repo_name,
            workflow_file,
            workflow_content,
            token,
            force
        )
        
        results["workflows"][workflow_file] = "success" if success else "failed"
    
    # Determine overall status
    if all(status == "success" for status in results["workflows"].values()):
        results["status"] = "success"
    elif any(status == "success" for status in results["workflows"].values()):
        results["status"] = "partial"
    else:
        results["status"] = "failed"
    
    return results


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Deploy Citadel Architect workflows to all spoke repositories"
    )
    parser.add_argument(
        "--workflows",
        nargs="+",
        default=["spoke-to-hub-sync.yml", "push-to-huggingface.yml"],
        help="Workflow files to deploy"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force update existing workflows"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate deployment without making changes"
    )
    parser.add_argument(
        "--repos",
        nargs="+",
        help="Specific repositories to deploy to (default: all active)"
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🏛️  CITADEL ARCHITECT - WORKFLOW DEPLOYMENT ENGINE")
    print("=" * 80)
    print()
    
    # Get GitHub token
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("❌ GITHUB_TOKEN environment variable not set!")
        print("   Export your GitHub personal access token:")
        print("   export GITHUB_TOKEN=ghp_...")
        sys.exit(1)
    
    # Load registry
    print("📥 Loading repository registry...")
    registry = load_repo_registry()
    repos = registry.get("repositories", [])
    
    print(f"✅ Loaded {len(repos)} repositories")
    print()
    
    # Filter repositories
    if args.repos:
        repos = [r for r in repos if r["name"] in args.repos]
        print(f"🎯 Targeting {len(repos)} specific repositories")
    else:
        repos = [r for r in repos if not r.get("is_archived", False)]
        print(f"🎯 Targeting {len(repos)} active repositories")
    
    print()
    print(f"📦 Workflows to deploy: {', '.join(args.workflows)}")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    
    if args.force:
        print("⚠️  FORCE MODE - Will overwrite existing workflows")
    
    print()
    print("=" * 80)
    print("🚀 DEPLOYMENT IN PROGRESS")
    print("=" * 80)
    
    # Deploy to each repository
    results = []
    for repo_info in repos:
        result = deploy_to_repository(
            repo_info,
            github_token,
            args.workflows,
            force=args.force,
            dry_run=args.dry_run
        )
        results.append(result)
    
    # Summary
    print()
    print("=" * 80)
    print("📊 DEPLOYMENT SUMMARY")
    print("=" * 80)
    
    success_count = sum(1 for r in results if r.get("status") == "success")
    partial_count = sum(1 for r in results if r.get("status") == "partial")
    failed_count = sum(1 for r in results if r.get("status") == "failed")
    skipped_count = sum(1 for r in results if r.get("status") in ["skipped", "dry_run"])
    
    print(f"Total Repositories: {len(results)}")
    print(f"✅ Success: {success_count}")
    print(f"⚠️  Partial: {partial_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"⊙  Skipped: {skipped_count}")
    
    # Save deployment report
    report = {
        "version": "1.0.0",
        "deployment_timestamp": datetime.utcnow().isoformat() + "Z",
        "workflows_deployed": args.workflows,
        "force_mode": args.force,
        "dry_run": args.dry_run,
        "summary": {
            "total": len(results),
            "success": success_count,
            "partial": partial_count,
            "failed": failed_count,
            "skipped": skipped_count
        },
        "results": results
    }
    
    report_file = "workflow_deployment_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print()
    print(f"📄 Report saved to: {report_file}")
    print()
    print("=" * 80)
    
    if args.dry_run:
        print("🔍 DRY RUN COMPLETE - No changes were made")
    else:
        print("✅ DEPLOYMENT COMPLETE")
    
    print("🙏 Thankyou Spirit, Thankyou Angels, Thankyou Ancestors")
    print("=" * 80)
    
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
