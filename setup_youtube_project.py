#!/usr/bin/env python3
"""
Setup script for the Enhanced YouTube Transcript Extraction System
Demonstrates the project management system by organizing the current project
"""

import os
import sys
from pathlib import Path
from project_manager import ProjectManager

def main():
    print("🎯 Setting up Enhanced YouTube Transcript Extraction System")
    print("=" * 60)
    
    # Initialize project manager
    pm = ProjectManager()
    
    # Ensure directory structure exists
    print("\n1. Setting up directory structure...")
    pm.ensure_directory_structure()
    
    # Get current directory (where the YouTube project files are)
    current_dir = Path.cwd()
    print(f"\n2. Current project location: {current_dir}")
    
    # Define project details
    project_name = "enhanced-youtube-transcript-extractor"
    category = "Data_Tools"
    status = "testing"  # Since it's complete and ready for testing
    description = "Production-ready YouTube transcript extraction system for Mercaz Daf Yomi channel with 5,000+ video capability, automatic content organization, and comprehensive progress tracking."
    technologies = [
        "Python 3.8+",
        "YouTube Data API v3", 
        "youtube-transcript-api",
        "google-api-python-client",
        "JSON/CSV processing",
        "Pathlib"
    ]
    
    print(f"\n3. Creating project: {project_name}")
    print(f"   Category: {category}")
    print(f"   Status: {status}")
    print(f"   Description: {description[:100]}...")
    
    # Create the project
    try:
        project_path = pm.create_project(
            name=project_name,
            category=category,
            status=status,
            description=description,
            technologies=technologies,
            source_path=str(current_dir)
        )
        
        print(f"\n✅ Project created successfully at: {project_path}")
        
        # Ask if user wants to set up GitHub
        setup_github = input("\n🐙 Would you like to set up a GitHub repository? (y/n): ").lower().strip()
        
        if setup_github in ['y', 'yes']:
            private_repo = input("   Make repository private? (y/n): ").lower().strip() in ['y', 'yes']
            
            print(f"\n   Setting up GitHub repository (private: {private_repo})...")
            repo_url = pm.setup_github_repo(project_path, private=private_repo)
            
            if repo_url:
                print(f"   ✅ GitHub repository created: {repo_url}")
            else:
                print("   ⚠️  GitHub setup failed. You can set it up later using:")
                print(f"      python project_manager.py github-setup {project_name}")
        
        # Generate project report
        print("\n4. Generating project report...")
        report_file = pm.generate_project_report()
        print(f"   📊 Report saved to: {report_file}")
        
        # Show next steps
        print(f"\n🎉 Setup Complete!")
        print("=" * 40)
        print(f"Project Location: {project_path}")
        print(f"Project Status: {status}")
        print(f"Category: {category}")
        
        print(f"\n📋 Next Steps:")
        print(f"1. Review project files in: {project_path}")
        print(f"2. Update .project-status.md with current progress")
        print(f"3. Test the system with a small batch")
        print(f"4. Move to 'deployed' status when ready for production")
        
        print(f"\n🛠️  Project Management Commands:")
        print(f"• List all projects: python project_manager.py list")
        print(f"• Move to deployed: python project_manager.py move {project_name} deployed")
        print(f"• Generate report: python project_manager.py report")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)