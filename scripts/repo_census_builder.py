#!/usr/bin/env python3
"""
🏛️ CITADEL OMNI-AUDIT: Repository Census Builder
Phase 1.1 - Complete inventory of all repos across GitHub and HuggingFace

Discovers all DJ-Goana-Coding (GitHub) and DJ-Goanna-Coding (HuggingFace) repos
Generates comprehensive repo matrix with metadata, languages, dependencies, and health metrics.
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import subprocess

class RepoCensusBuilder:
    """Builds comprehensive census of all repositories across both namespaces"""
    
    def __init__(self):
        self.github_org = "DJ-Goana-Coding"
        self.hf_org = "DJ-Goanna-Coding"
        self.github_token = os.getenv("GITHUB_TOKEN", os.getenv("GH_TOKEN"))
        self.hf_token = os.getenv("HF_TOKEN")
        self.output_dir = Path("/home/runner/work/mapping-and-inventory/mapping-and-inventory/data/discoveries")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.census_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "github_repos": [],
            "huggingface_spaces": [],
            "summary": {
                "total_github_repos": 0,
                "total_hf_spaces": 0,
                "total_repositories": 0,
                "primary_languages": {},
                "repos_with_tests": 0,
                "repos_with_ci": 0,
                "repos_with_docs": 0
            }
        }
    
    def discover_github_repos(self) -> List[Dict]:
        """Discover all repositories in DJ-Goana-Coding organization"""
        print(f"🔍 Discovering GitHub repositories for {self.github_org}...")
        
        headers = {}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        
        repos = []
        page = 1
        
        while True:
            url = f"https://api.github.com/orgs/{self.github_org}/repos"
            params = {"per_page": 100, "page": page, "sort": "updated", "direction": "desc"}
            
            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                batch = response.json()
                
                if not batch:
                    break
                
                for repo in batch:
                    repo_info = self._analyze_github_repo(repo, headers)
                    repos.append(repo_info)
                    print(f"  ✓ {repo['name']} - {repo_info['primary_language']} - {repo_info['size_kb']}KB")
                
                page += 1
                
                # Check rate limit
                if 'X-RateLimit-Remaining' in response.headers:
                    remaining = int(response.headers['X-RateLimit-Remaining'])
                    if remaining < 10:
                        print(f"⚠️  GitHub rate limit low: {remaining} remaining")
                        break
                        
            except Exception as e:
                print(f"❌ Error fetching GitHub repos (page {page}): {e}")
                break
        
        print(f"✅ Discovered {len(repos)} GitHub repositories")
        return repos
    
    def _analyze_github_repo(self, repo: Dict, headers: Dict) -> Dict:
        """Analyze individual GitHub repository"""
        repo_data = {
            "name": repo["name"],
            "full_name": repo["full_name"],
            "url": repo["html_url"],
            "primary_language": repo.get("language", "Unknown"),
            "size_kb": repo.get("size", 0),
            "last_activity": repo.get("updated_at", ""),
            "created_at": repo.get("created_at", ""),
            "default_branch": repo.get("default_branch", "main"),
            "has_issues": repo.get("has_issues", False),
            "has_wiki": repo.get("has_wiki", False),
            "has_pages": repo.get("has_pages", False),
            "open_issues_count": repo.get("open_issues_count", 0),
            "stargazers_count": repo.get("stargazers_count", 0),
            "forks_count": repo.get("forks_count", 0),
            "archived": repo.get("archived", False),
            "disabled": repo.get("disabled", False),
            "dependencies": [],
            "has_ci": False,
            "has_tests": False,
            "has_readme": False,
            "documentation_score": 0
        }
        
        # Check for dependency manifests
        manifest_files = [
            "requirements.txt", "package.json", "Gemfile", "go.mod", 
            "Cargo.toml", "pom.xml", "build.gradle", "composer.json"
        ]
        
        # Check for CI/CD configs
        ci_files = [
            ".github/workflows", ".gitlab-ci.yml", ".travis.yml", 
            "Jenkinsfile", ".circleci/config.yml"
        ]
        
        # Check for test directories
        test_indicators = [
            "tests/", "test/", "__tests__/", "spec/", 
            "pytest.ini", "jest.config.js", "phpunit.xml"
        ]
        
        # Check for documentation
        doc_indicators = [
            "README.md", "docs/", "CONTRIBUTING.md", 
            "LICENSE", "CHANGELOG.md"
        ]
        
        try:
            # Get repository contents to check for key files
            contents_url = f"https://api.github.com/repos/{repo['full_name']}/contents"
            response = requests.get(contents_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                contents = response.json()
                file_names = [item["name"] for item in contents if isinstance(contents, list)]
                
                # Check for dependency manifests
                for manifest in manifest_files:
                    if manifest in file_names:
                        repo_data["dependencies"].append(manifest)
                
                # Check for CI
                if ".github" in file_names or any(ci in file_names for ci in ci_files):
                    repo_data["has_ci"] = True
                
                # Check for tests
                if any(test in file_names or any(test in f for f in file_names) for test in test_indicators):
                    repo_data["has_tests"] = True
                
                # Documentation score
                doc_count = sum(1 for doc in doc_indicators if doc in file_names or any(doc in f for f in file_names))
                repo_data["documentation_score"] = (doc_count / len(doc_indicators)) * 100
                repo_data["has_readme"] = "README.md" in file_names
                
        except Exception as e:
            print(f"  ⚠️  Could not analyze {repo['name']}: {e}")
        
        return repo_data
    
    def discover_huggingface_spaces(self) -> List[Dict]:
        """Discover all HuggingFace Spaces in DJ-Goanna-Coding namespace"""
        print(f"🔍 Discovering HuggingFace Spaces for {self.hf_org}...")
        
        spaces = []
        headers = {}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"
        
        try:
            # HuggingFace API for listing spaces
            url = f"https://huggingface.co/api/spaces/{self.hf_org}"
            response = requests.get(url, headers=headers, timeout=30)
            
            # Alternative: Try direct listing
            url = f"https://huggingface.co/api/models?author={self.hf_org}"
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                # Process spaces/models
                for item in data if isinstance(data, list) else []:
                    space_info = {
                        "name": item.get("id", "").split("/")[-1],
                        "full_name": item.get("id", ""),
                        "url": f"https://huggingface.co/{item.get('id', '')}",
                        "type": item.get("_type", "unknown"),
                        "last_modified": item.get("lastModified", ""),
                        "likes": item.get("likes", 0),
                        "sdk": item.get("sdk", "unknown"),
                        "tags": item.get("tags", [])
                    }
                    spaces.append(space_info)
                    print(f"  ✓ {space_info['name']} - {space_info['type']}")
            
        except Exception as e:
            print(f"⚠️  Could not fetch HuggingFace spaces: {e}")
            print("  (This is expected if namespace has no public spaces or API access is limited)")
        
        print(f"✅ Discovered {len(spaces)} HuggingFace Spaces/Models")
        return spaces
    
    def generate_summary_statistics(self):
        """Generate summary statistics from census data"""
        github_repos = self.census_data["github_repos"]
        hf_spaces = self.census_data["huggingface_spaces"]
        
        # Count totals
        self.census_data["summary"]["total_github_repos"] = len(github_repos)
        self.census_data["summary"]["total_hf_spaces"] = len(hf_spaces)
        self.census_data["summary"]["total_repositories"] = len(github_repos) + len(hf_spaces)
        
        # Language distribution
        language_counts = {}
        for repo in github_repos:
            lang = repo.get("primary_language", "Unknown")
            language_counts[lang] = language_counts.get(lang, 0) + 1
        self.census_data["summary"]["primary_languages"] = language_counts
        
        # Feature counts
        self.census_data["summary"]["repos_with_tests"] = sum(1 for r in github_repos if r.get("has_tests"))
        self.census_data["summary"]["repos_with_ci"] = sum(1 for r in github_repos if r.get("has_ci"))
        self.census_data["summary"]["repos_with_docs"] = sum(1 for r in github_repos if r.get("has_readme"))
        
        # Average documentation score
        doc_scores = [r.get("documentation_score", 0) for r in github_repos]
        self.census_data["summary"]["avg_documentation_score"] = sum(doc_scores) / len(doc_scores) if doc_scores else 0
        
        # Size statistics
        total_size_kb = sum(r.get("size_kb", 0) for r in github_repos)
        self.census_data["summary"]["total_size_kb"] = total_size_kb
        self.census_data["summary"]["total_size_mb"] = round(total_size_kb / 1024, 2)
    
    def build_census(self):
        """Build complete repository census"""
        print("🏛️ CITADEL OMNI-AUDIT: Repository Census Builder")
        print("=" * 60)
        
        # Discover GitHub repositories
        self.census_data["github_repos"] = self.discover_github_repos()
        
        # Discover HuggingFace Spaces
        self.census_data["huggingface_spaces"] = self.discover_huggingface_spaces()
        
        # Generate summary statistics
        self.generate_summary_statistics()
        
        # Save census data
        output_file = self.output_dir / "repo_census.json"
        with open(output_file, 'w') as f:
            json.dump(self.census_data, f, indent=2)
        
        print("\n" + "=" * 60)
        print("📊 CENSUS SUMMARY")
        print("=" * 60)
        print(f"GitHub Repositories: {self.census_data['summary']['total_github_repos']}")
        print(f"HuggingFace Spaces: {self.census_data['summary']['total_hf_spaces']}")
        print(f"Total Repositories: {self.census_data['summary']['total_repositories']}")
        print(f"Total Size: {self.census_data['summary']['total_size_mb']} MB")
        print(f"\nRepos with Tests: {self.census_data['summary']['repos_with_tests']}")
        print(f"Repos with CI/CD: {self.census_data['summary']['repos_with_ci']}")
        print(f"Repos with Docs: {self.census_data['summary']['repos_with_docs']}")
        print(f"Avg Doc Score: {self.census_data['summary']['avg_documentation_score']:.1f}%")
        print(f"\nLanguage Distribution:")
        for lang, count in sorted(self.census_data['summary']['primary_languages'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {lang}: {count}")
        print(f"\n✅ Census saved to: {output_file}")
        
        return self.census_data


if __name__ == "__main__":
    builder = RepoCensusBuilder()
    census = builder.build_census()
