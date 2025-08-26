#!/usr/bin/env python3
"""
Project Management System
Automates project organization following the File Organization System
Includes GitHub integration and project lifecycle management
"""

import os
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse

class ProjectManager:
    def __init__(self, base_path: str = None):
        """Initialize the Project Manager with base desktop path"""
        if base_path:
            self.desktop_path = Path(base_path)
        else:
            # Default to Desktop path
            home = Path.home()
            self.desktop_path = home / "Desktop"
        
        # Define status directories
        self.status_dirs = {
            "active": self.desktop_path / "01_Active_Projects",
            "testing": self.desktop_path / "02_Testing_Review", 
            "deployed": self.desktop_path / "03_Deployed_Live",
            "archived": self.desktop_path / "04_Archived",
            "resources": self.desktop_path / "00_Resources"
        }
        
        # Define category directories
        self.categories = [
            "Web_Applications",
            "Data_Tools", 
            "Educational_Content",
            "Specialized_Platforms",
            "AI_Development",
            "Technical_Tools",
            "Publishing"
        ]
        
        # Project templates
        self.project_template = {
            "name": "",
            "category": "",
            "status": "active",
            "description": "",
            "created_date": "",
            "last_updated": "",
            "github_repo": "",
            "technologies": [],
            "next_steps": [],
            "notes": ""
        }

    def ensure_directory_structure(self):
        """Ensure all required directories exist"""
        print("🏗️  Ensuring directory structure...")
        
        # Create main status directories
        for status, path in self.status_dirs.items():
            path.mkdir(exist_ok=True)
            print(f"✅ {status}: {path}")
            
            # Create category subdirectories (except resources)
            if status != "resources":
                for category in self.categories:
                    category_path = path / category
                    category_path.mkdir(exist_ok=True)
                    print(f"   📁 {category}")
        
        # Create resources subdirectories
        resources_subdirs = [
            "Templates",
            "Documentation", 
            "Scripts",
            "Assets",
            "Configurations"
        ]
        
        for subdir in resources_subdirs:
            subdir_path = self.status_dirs["resources"] / subdir
            subdir_path.mkdir(exist_ok=True)
            print(f"📚 Resources/{subdir}")

    def create_project(self, name: str, category: str, status: str = "active", 
                      description: str = "", technologies: List[str] = None,
                      github_repo: str = "", source_path: str = None) -> Path:
        """Create a new project with proper structure"""
        
        if technologies is None:
            technologies = []
            
        # Validate inputs
        if status not in self.status_dirs:
            raise ValueError(f"Invalid status: {status}. Must be one of: {list(self.status_dirs.keys())}")
        
        if category not in self.categories:
            raise ValueError(f"Invalid category: {category}. Must be one of: {self.categories}")
        
        # Create project directory
        project_path = self.status_dirs[status] / category / name
        
        if project_path.exists():
            print(f"⚠️  Project already exists: {project_path}")
            return project_path
        
        project_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created project directory: {project_path}")
        
        # Copy source files if provided
        if source_path and Path(source_path).exists():
            source = Path(source_path)
            print(f"📋 Copying files from: {source}")
            
            for item in source.iterdir():
                if item.is_file():
                    shutil.copy2(item, project_path)
                    print(f"   📄 {item.name}")
                elif item.is_dir() and item.name not in ['.git', '__pycache__', 'node_modules']:
                    shutil.copytree(item, project_path / item.name, dirs_exist_ok=True)
                    print(f"   📁 {item.name}/")
        
        # Create standard project structure
        self._create_project_structure(project_path)
        
        # Create project metadata
        project_info = self.project_template.copy()
        project_info.update({
            "name": name,
            "category": category,
            "status": status,
            "description": description,
            "created_date": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "github_repo": github_repo,
            "technologies": technologies
        })
        
        # Save project metadata
        self._save_project_metadata(project_path, project_info)
        
        # Create README if it doesn't exist
        self._create_readme(project_path, project_info)
        
        # Create project status file
        self._create_project_status(project_path, project_info)
        
        print(f"✅ Project '{name}' created successfully!")
        return project_path

    def _create_project_structure(self, project_path: Path):
        """Create standard project directory structure"""
        standard_dirs = [
            "docs",
            "src", 
            "tests",
            "assets",
            "scripts",
            "config"
        ]
        
        for dir_name in standard_dirs:
            dir_path = project_path / dir_name
            dir_path.mkdir(exist_ok=True)
        
        # Create .env.example if it doesn't exist
        env_example = project_path / ".env.example"
        if not env_example.exists():
            env_example.write_text("# Environment variables template\n# Copy to .env and fill in values\n")

    def _save_project_metadata(self, project_path: Path, project_info: Dict):
        """Save project metadata to .project-metadata.json"""
        metadata_file = project_path / ".project-metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(project_info, f, indent=2, ensure_ascii=False)

    def _create_readme(self, project_path: Path, project_info: Dict):
        """Create README.md if it doesn't exist"""
        readme_path = project_path / "README.md"
        if readme_path.exists():
            return
            
        readme_content = f"""# {project_info['name']}

## Overview
{project_info['description'] or 'Project description goes here.'}

## Technologies
{chr(10).join(f'- {tech}' for tech in project_info['technologies']) if project_info['technologies'] else '- List technologies used'}

## Setup Instructions

1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Install dependencies
4. Run the application

## Project Structure

```
{project_info['name']}/
├── README.md                 # This file
├── .env.example             # Environment variables template
├── .project-metadata.json   # Project metadata
├── .project-status.md       # Current status and next steps
├── docs/                    # Documentation
├── src/                     # Source code
├── tests/                   # Test files
├── assets/                  # Images, fonts, etc.
├── scripts/                 # Build/deployment scripts
└── config/                  # Configuration files
```

## Status
- **Category**: {project_info['category']}
- **Status**: {project_info['status']}
- **Created**: {project_info['created_date'][:10]}
- **GitHub**: {project_info['github_repo'] or 'Not yet created'}

## Next Steps
See `.project-status.md` for current status and next steps.

---
Created: {datetime.now().strftime('%Y-%m-%d')}
"""
        readme_path.write_text(readme_content, encoding='utf-8')

    def _create_project_status(self, project_path: Path, project_info: Dict):
        """Create .project-status.md file"""
        status_path = project_path / ".project-status.md"
        
        status_content = f"""# Project Status: {project_info['name']}

## Current Status: {project_info['status'].title()}

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Next Steps
- [ ] Define project requirements
- [ ] Set up development environment
- [ ] Create initial implementation
- [ ] Add tests
- [ ] Create documentation
- [ ] Set up GitHub repository
- [ ] Deploy/publish

## Recent Updates
- {datetime.now().strftime('%Y-%m-%d')}: Project created

## Notes
{project_info['notes'] or 'Add project notes here...'}

## GitHub Repository
{project_info['github_repo'] or 'Not yet created - use `python project_manager.py github-setup` to create'}

---
**Project Path**: `{project_path}`  
**Category**: {project_info['category']}  
**Technologies**: {', '.join(project_info['technologies']) if project_info['technologies'] else 'Not specified'}
"""
        status_path.write_text(status_content, encoding='utf-8')

    def move_project(self, project_name: str, new_status: str, new_category: str = None):
        """Move project to different status/category"""
        # Find current project location
        current_path = self._find_project(project_name)
        if not current_path:
            print(f"❌ Project '{project_name}' not found")
            return False
        
        # Determine new location
        if new_category is None:
            new_category = current_path.parent.name
        
        new_path = self.status_dirs[new_status] / new_category / project_name
        
        if new_path.exists():
            print(f"❌ Target location already exists: {new_path}")
            return False
        
        # Move project
        new_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(current_path), str(new_path))
        
        # Update metadata
        self._update_project_metadata(new_path, {"status": new_status, "category": new_category})
        
        print(f"✅ Moved '{project_name}' from {current_path} to {new_path}")
        return True

    def _find_project(self, project_name: str) -> Optional[Path]:
        """Find project by name across all status directories"""
        for status_path in self.status_dirs.values():
            if not status_path.exists():
                continue
            for category_path in status_path.iterdir():
                if category_path.is_dir():
                    project_path = category_path / project_name
                    if project_path.exists():
                        return project_path
        return None

    def _update_project_metadata(self, project_path: Path, updates: Dict):
        """Update project metadata"""
        metadata_file = project_path / ".project-metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            metadata.update(updates)
            metadata["last_updated"] = datetime.now().isoformat()
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

    def setup_github_repo(self, project_path: Path, repo_name: str = None, private: bool = True):
        """Set up GitHub repository for project"""
        if repo_name is None:
            repo_name = project_path.name
        
        print(f"🐙 Setting up GitHub repository: {repo_name}")
        
        try:
            # Initialize git if not already done
            if not (project_path / ".git").exists():
                subprocess.run(["git", "init"], cwd=project_path, check=True)
                print("✅ Git repository initialized")
            
            # Create .gitignore if it doesn't exist
            gitignore_path = project_path / ".gitignore"
            if not gitignore_path.exists():
                gitignore_content = """# Dependencies
node_modules/
__pycache__/
*.pyc
venv/
env/

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Build outputs
dist/
build/
*.egg-info/

# Project specific
.project-metadata.json
"""
                gitignore_path.write_text(gitignore_content)
                print("✅ .gitignore created")
            
            # Add all files
            subprocess.run(["git", "add", "."], cwd=project_path, check=True)
            
            # Initial commit
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=project_path, check=True)
            print("✅ Initial commit created")
            
            # Create GitHub repository using GitHub CLI
            privacy_flag = "--private" if private else "--public"
            result = subprocess.run([
                "gh", "repo", "create", repo_name, 
                privacy_flag, 
                "--source=.", 
                "--remote=origin", 
                "--push"
            ], cwd=project_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                repo_url = f"https://github.com/{self._get_github_username()}/{repo_name}"
                print(f"✅ GitHub repository created: {repo_url}")
                
                # Update project metadata
                self._update_project_metadata(project_path, {"github_repo": repo_url})
                
                return repo_url
            else:
                print(f"❌ Failed to create GitHub repository: {result.stderr}")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Git/GitHub operation failed: {e}")
            return None
        except FileNotFoundError:
            print("❌ GitHub CLI (gh) not found. Please install it first.")
            print("   Visit: https://cli.github.com/")
            return None

    def _get_github_username(self) -> str:
        """Get GitHub username from git config"""
        try:
            result = subprocess.run(["git", "config", "user.name"], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except:
            return "your-username"

    def list_projects(self, status: str = None, category: str = None):
        """List all projects with optional filtering"""
        print("📋 Project Inventory")
        print("=" * 50)
        
        status_dirs_to_check = [status] if status else self.status_dirs.keys()
        
        for status_name in status_dirs_to_check:
            if status_name == "resources":
                continue
                
            status_path = self.status_dirs[status_name]
            if not status_path.exists():
                continue
                
            print(f"\n🏷️  {status_name.upper().replace('_', ' ')}")
            print("-" * 30)
            
            categories_to_check = [category] if category else self.categories
            
            for cat in categories_to_check:
                cat_path = status_path / cat
                if not cat_path.exists():
                    continue
                    
                projects = [p for p in cat_path.iterdir() if p.is_dir()]
                if projects:
                    print(f"\n  📁 {cat}:")
                    for project in sorted(projects):
                        metadata_file = project / ".project-metadata.json"
                        if metadata_file.exists():
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                            desc = metadata.get('description', 'No description')[:50]
                            if len(desc) == 50:
                                desc += "..."
                            print(f"    • {project.name} - {desc}")
                        else:
                            print(f"    • {project.name}")

    def generate_project_report(self, output_file: str = None):
        """Generate comprehensive project report"""
        if output_file is None:
            output_file = self.desktop_path / f"Project_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        report_content = f"""# Project Portfolio Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

"""
        
        # Count projects by status and category
        status_counts = {}
        category_counts = {}
        total_projects = 0
        
        for status_name, status_path in self.status_dirs.items():
            if status_name == "resources" or not status_path.exists():
                continue
                
            status_count = 0
            for cat in self.categories:
                cat_path = status_path / cat
                if cat_path.exists():
                    projects = [p for p in cat_path.iterdir() if p.is_dir()]
                    count = len(projects)
                    status_count += count
                    category_counts[cat] = category_counts.get(cat, 0) + count
            
            status_counts[status_name] = status_count
            total_projects += status_count
        
        report_content += f"**Total Projects**: {total_projects}\n\n"
        
        # Status breakdown
        report_content += "### By Status\n"
        for status, count in status_counts.items():
            report_content += f"- **{status.replace('_', ' ').title()}**: {count}\n"
        
        # Category breakdown
        report_content += "\n### By Category\n"
        for category, count in sorted(category_counts.items()):
            report_content += f"- **{category.replace('_', ' ')}**: {count}\n"
        
        # Detailed project listings
        report_content += "\n## Detailed Project Listings\n\n"
        
        for status_name, status_path in self.status_dirs.items():
            if status_name == "resources" or not status_path.exists():
                continue
                
            report_content += f"### {status_name.replace('_', ' ').title()}\n\n"
            
            for cat in self.categories:
                cat_path = status_path / cat
                if not cat_path.exists():
                    continue
                    
                projects = [p for p in cat_path.iterdir() if p.is_dir()]
                if projects:
                    report_content += f"#### {cat.replace('_', ' ')}\n\n"
                    for project in sorted(projects):
                        metadata_file = project / ".project-metadata.json"
                        if metadata_file.exists():
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                            
                            report_content += f"**{project.name}**\n"
                            report_content += f"- Description: {metadata.get('description', 'No description')}\n"
                            report_content += f"- Created: {metadata.get('created_date', 'Unknown')[:10]}\n"
                            report_content += f"- Technologies: {', '.join(metadata.get('technologies', []))}\n"
                            if metadata.get('github_repo'):
                                report_content += f"- GitHub: {metadata['github_repo']}\n"
                            report_content += f"- Path: `{project}`\n\n"
                        else:
                            report_content += f"**{project.name}**\n"
                            report_content += f"- Path: `{project}`\n\n"
        
        # Write report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📊 Project report generated: {output_file}")
        return output_file


def main():
    parser = argparse.ArgumentParser(description="Project Management System")
    parser.add_argument("--base-path", help="Base path for project organization (default: ~/Desktop)")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Set up directory structure")
    
    # Create project command
    create_parser = subparsers.add_parser("create", help="Create new project")
    create_parser.add_argument("name", help="Project name")
    create_parser.add_argument("category", help="Project category")
    create_parser.add_argument("--status", default="active", help="Project status")
    create_parser.add_argument("--description", help="Project description")
    create_parser.add_argument("--source", help="Source directory to copy from")
    create_parser.add_argument("--github", action="store_true", help="Create GitHub repository")
    create_parser.add_argument("--private", action="store_true", help="Make GitHub repo private")
    
    # Move project command
    move_parser = subparsers.add_parser("move", help="Move project to different status")
    move_parser.add_argument("name", help="Project name")
    move_parser.add_argument("status", help="New status")
    move_parser.add_argument("--category", help="New category (optional)")
    
    # List projects command
    list_parser = subparsers.add_parser("list", help="List projects")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--category", help="Filter by category")
    
    # GitHub setup command
    github_parser = subparsers.add_parser("github-setup", help="Set up GitHub for existing project")
    github_parser.add_argument("name", help="Project name")
    github_parser.add_argument("--private", action="store_true", help="Make repo private")
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate project report")
    report_parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize project manager
    pm = ProjectManager(args.base_path)
    
    if args.command == "setup":
        pm.ensure_directory_structure()
    
    elif args.command == "create":
        project_path = pm.create_project(
            name=args.name,
            category=args.category,
            status=args.status,
            description=args.description or "",
            source_path=args.source
        )
        
        if args.github:
            pm.setup_github_repo(project_path, private=args.private)
    
    elif args.command == "move":
        pm.move_project(args.name, args.status, args.category)
    
    elif args.command == "list":
        pm.list_projects(args.status, args.category)
    
    elif args.command == "github-setup":
        project_path = pm._find_project(args.name)
        if project_path:
            pm.setup_github_repo(project_path, private=args.private)
        else:
            print(f"❌ Project '{args.name}' not found")
    
    elif args.command == "report":
        pm.generate_project_report(args.output)


if __name__ == "__main__":
    main()