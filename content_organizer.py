#!/usr/bin/env python3
"""
Content Organization Utility for Mercaz Daf Yomi Transcripts
Organizes extracted transcripts into proper directory structure and generates reports.
"""

import os
import json
import csv
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import re
import argparse


class ContentOrganizer:
    """Utility for organizing and managing extracted transcript content."""
    
    def __init__(self, base_directory: str = "Mercaz_Daf_Yomi_Transcripts"):
        """Initialize with base directory path."""
        self.base_dir = Path(base_directory)
        self.tractate_patterns = {
            "Berachos": ["berachos", "berakhot", "brachot"],
            "Shabbos": ["shabbos", "shabbat"],
            "Eruvin": ["eruvin"],
            "Pesachim": ["pesachim"],
            "Shekalim": ["shekalim"],
            "Yoma": ["yoma"],
            "Sukkah": ["sukkah"],
            "Beitzah": ["beitzah", "beitza"],
            "Rosh_Hashanah": ["rosh hashanah", "rosh_hashanah"],
            "Taanis": ["taanis", "taanit"],
            "Megillah": ["megillah"],
            "Moed_Katan": ["moed katan", "moed_katan"],
            "Chagigah": ["chagigah"],
            "Yevamos": ["yevamos", "yevamot"],
            "Kesubos": ["kesubos", "ketubbot"],
            "Nedarim": ["nedarim"],
            "Nazir": ["nazir"],
            "Sotah": ["sotah"],
            "Gittin": ["gittin"],
            "Kiddushin": ["kiddushin"],
            "Bava_Kamma": ["bava kamma", "bava_kamma"],
            "Bava_Metzia": ["bava metzia", "bava_metzia"],
            "Bava_Basra": ["bava basra", "bava_basra"],
            "Sanhedrin": ["sanhedrin"],
            "Makkos": ["makkos", "makkot"],
            "Shevuos": ["shevuos", "shevuot"],
            "Avodah_Zarah": ["avodah zarah", "avodah_zarah"],
            "Horayos": ["horayos", "horayot"],
            "Zevachim": ["zevachim"],
            "Menachos": ["menachos", "menachot"],
            "Chullin": ["chullin"],
            "Bechorot": ["bechorot", "bechoros"],
            "Arachin": ["arachin"],
            "Temurah": ["temurah"],
            "Kerisos": ["kerisos", "keritot"],
            "Meilah": ["meilah"],
            "Kinnim": ["kinnim"],
            "Tamid": ["tamid"],
            "Midos": ["midos", "midot"],
            "Niddah": ["niddah"]
        }
        
        self.series_types = {
            "Daf_Yomi": ["daf yomi"],
            "Shiurim": ["shiur"],
            "Lectures": ["lecture"],
            "Special_Series": ["special", "event", "announcement"],
            "General": []
        }
    
    def create_directory_structure(self):
        """Create the organized directory structure."""
        print("Creating directory structure...")
        
        # Create base directory
        self.base_dir.mkdir(exist_ok=True)
        
        # Create tractate directories
        for tractate in self.tractate_patterns.keys():
            tractate_dir = self.base_dir / tractate
            tractate_dir.mkdir(exist_ok=True)
            
            # Create series subdirectories
            for series_type in self.series_types.keys():
                series_dir = tractate_dir / series_type
                series_dir.mkdir(exist_ok=True)
        
        # Create special directories
        special_dirs = ["Unclassified", "Special_Series", "Logs", "Reports"]
        for special_dir in special_dirs:
            (self.base_dir / special_dir).mkdir(exist_ok=True)
            
            # Create series subdirectories for special dirs
            if special_dir in ["Unclassified", "Special_Series"]:
                for series_type in self.series_types.keys():
                    (self.base_dir / special_dir / series_type).mkdir(exist_ok=True)
        
        print(f"Directory structure created in: {self.base_dir}")
    
    def classify_content(self, title: str, description: str = "") -> Tuple[str, str]:
        """Classify content by tractate and series type."""
        title_lower = title.lower()
        description_lower = description.lower()
        combined_text = f"{title_lower} {description_lower}"
        
        # Find tractate
        tractate = "Unclassified"
        for tract_name, patterns in self.tractate_patterns.items():
            if any(pattern in combined_text for pattern in patterns):
                tractate = tract_name
                break
        
        # Find series type
        series_type = "General"
        for series_name, patterns in self.series_types.items():
            if patterns and any(pattern in combined_text for pattern in patterns):
                series_type = series_name
                break
        
        # Special handling for certain patterns
        if any(word in combined_text for word in ['special', 'event', 'announcement']):
            tractate = "Special_Series"
            series_type = "Events"
        
        return tractate, series_type
    
    def organize_existing_files(self, source_directory: str = None):
        """Organize existing transcript files into proper structure."""
        if source_directory:
            source_path = Path(source_directory)
        else:
            source_path = self.base_dir
        
        if not source_path.exists():
            print(f"Source directory not found: {source_path}")
            return
        
        print(f"Organizing files from: {source_path}")
        
        # Find all transcript files
        transcript_files = []
        for ext in ['*.txt', '*.json']:
            transcript_files.extend(source_path.glob(f"**/{ext}"))
        
        organized_count = 0
        failed_count = 0
        
        for file_path in transcript_files:
            try:
                # Skip if already in organized structure
                if len(file_path.parts) > 2 and file_path.parts[-3] in self.tractate_patterns:
                    continue
                
                # Extract title from filename or file content
                title = self.extract_title_from_file(file_path)
                if not title:
                    title = file_path.stem
                
                # Classify content
                tractate, series_type = self.classify_content(title)
                
                # Create target directory
                target_dir = self.base_dir / tractate / series_type
                target_dir.mkdir(parents=True, exist_ok=True)
                
                # Move file
                target_path = target_dir / file_path.name
                if target_path != file_path:
                    shutil.move(str(file_path), str(target_path))
                    organized_count += 1
                    print(f"Moved: {file_path.name} -> {tractate}/{series_type}/")
                
            except Exception as e:
                print(f"Failed to organize {file_path.name}: {e}")
                failed_count += 1
        
        print(f"Organization complete: {organized_count} files organized, {failed_count} failed")
    
    def extract_title_from_file(self, file_path: Path) -> str:
        """Extract title from transcript file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_lines = f.read(500)  # Read first 500 characters
                
                # Look for title line
                for line in first_lines.split('\n'):
                    if line.startswith('Title:'):
                        return line.replace('Title:', '').strip()
                    elif line.startswith('Video:'):
                        return line.replace('Video:', '').strip()
                
                # Fallback to filename
                return file_path.stem
                
        except Exception:
            return file_path.stem
    
    def generate_content_inventory(self) -> Dict:
        """Generate comprehensive inventory of organized content."""
        inventory = {
            'total_files': 0,
            'tractates': {},
            'series_breakdown': {},
            'file_types': {},
            'size_stats': {},
            'generated_at': datetime.now().isoformat()
        }
        
        print("Generating content inventory...")
        
        total_size = 0
        file_sizes = []
        
        for tractate_dir in self.base_dir.iterdir():
            if not tractate_dir.is_dir() or tractate_dir.name in ['Logs', 'Reports']:
                continue
            
            tractate_name = tractate_dir.name
            inventory['tractates'][tractate_name] = {
                'total_files': 0,
                'series': {},
                'total_size': 0
            }
            
            for series_dir in tractate_dir.iterdir():
                if not series_dir.is_dir():
                    continue
                
                series_name = series_dir.name
                series_files = list(series_dir.glob('*'))
                series_count = len([f for f in series_files if f.is_file()])
                series_size = sum(f.stat().st_size for f in series_files if f.is_file())
                
                inventory['tractates'][tractate_name]['series'][series_name] = {
                    'file_count': series_count,
                    'total_size': series_size
                }
                
                inventory['tractates'][tractate_name]['total_files'] += series_count
                inventory['tractates'][tractate_name]['total_size'] += series_size
                
                # Update series breakdown
                if series_name not in inventory['series_breakdown']:
                    inventory['series_breakdown'][series_name] = 0
                inventory['series_breakdown'][series_name] += series_count
                
                # Track file types and sizes
                for file_path in series_files:
                    if file_path.is_file():
                        ext = file_path.suffix.lower()
                        inventory['file_types'][ext] = inventory['file_types'].get(ext, 0) + 1
                        
                        file_size = file_path.stat().st_size
                        file_sizes.append(file_size)
                        total_size += file_size
            
            inventory['total_files'] += inventory['tractates'][tractate_name]['total_files']
        
        # Calculate size statistics
        if file_sizes:
            inventory['size_stats'] = {
                'total_size_mb': total_size / (1024 * 1024),
                'average_file_size_kb': (sum(file_sizes) / len(file_sizes)) / 1024,
                'largest_file_mb': max(file_sizes) / (1024 * 1024),
                'smallest_file_kb': min(file_sizes) / 1024
            }
        
        return inventory
    
    def create_tractate_indexes(self):
        """Create index files for each tractate."""
        print("Creating tractate indexes...")
        
        for tractate_dir in self.base_dir.iterdir():
            if not tractate_dir.is_dir() or tractate_dir.name in ['Logs', 'Reports', 'Unclassified']:
                continue
            
            tractate_name = tractate_dir.name
            index_file = tractate_dir / f"{tractate_name}_INDEX.md"
            
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(f"# {tractate_name} - Transcript Index\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                total_files = 0
                
                for series_dir in sorted(tractate_dir.iterdir()):
                    if not series_dir.is_dir():
                        continue
                    
                    series_name = series_dir.name
                    transcript_files = [f for f in series_dir.iterdir() if f.is_file() and f.suffix in ['.txt', '.json']]
                    
                    if transcript_files:
                        f.write(f"## {series_name} ({len(transcript_files)} files)\n\n")
                        
                        for transcript_file in sorted(transcript_files):
                            # Extract basic info
                            title = self.extract_title_from_file(transcript_file)
                            file_size = transcript_file.stat().st_size / 1024  # KB
                            
                            f.write(f"- **{title}**\n")
                            f.write(f"  - File: `{transcript_file.name}`\n")
                            f.write(f"  - Size: {file_size:.1f} KB\n")
                            f.write(f"  - Path: `{series_name}/{transcript_file.name}`\n\n")
                        
                        total_files += len(transcript_files)
                
                f.write(f"\n---\n**Total Files in {tractate_name}: {total_files}**\n")
        
        print("Tractate indexes created")
    
    def generate_master_index(self):
        """Generate master index of all content."""
        master_index_file = self.base_dir / "MASTER_INDEX.md"
        
        print("Generating master index...")
        
        with open(master_index_file, 'w', encoding='utf-8') as f:
            f.write("# Mercaz Daf Yomi - Master Transcript Index\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            inventory = self.generate_content_inventory()
            
            f.write("## Summary Statistics\n\n")
            f.write(f"- **Total Files**: {inventory['total_files']}\n")
            f.write(f"- **Total Size**: {inventory['size_stats'].get('total_size_mb', 0):.1f} MB\n")
            f.write(f"- **Average File Size**: {inventory['size_stats'].get('average_file_size_kb', 0):.1f} KB\n")
            f.write(f"- **Tractates Covered**: {len(inventory['tractates'])}\n\n")
            
            f.write("## Tractate Breakdown\n\n")
            for tractate, data in sorted(inventory['tractates'].items()):
                f.write(f"### {tractate} ({data['total_files']} files)\n\n")
                
                for series, series_data in sorted(data['series'].items()):
                    if series_data['file_count'] > 0:
                        f.write(f"- **{series}**: {series_data['file_count']} files "
                               f"({series_data['total_size']/1024:.1f} KB)\n")
                f.write("\n")
            
            f.write("## Series Type Summary\n\n")
            for series_type, count in sorted(inventory['series_breakdown'].items()):
                f.write(f"- **{series_type}**: {count} files\n")
            
            f.write("\n## File Type Breakdown\n\n")
            for file_type, count in sorted(inventory['file_types'].items()):
                f.write(f"- **{file_type}**: {count} files\n")
            
            f.write("\n## Directory Structure\n\n")
            f.write("```\n")
            f.write("Mercaz_Daf_Yomi_Transcripts/\n")
            for tractate in sorted(inventory['tractates'].keys()):
                f.write(f"├── {tractate}/\n")
                for series in sorted(inventory['tractates'][tractate]['series'].keys()):
                    if inventory['tractates'][tractate]['series'][series]['file_count'] > 0:
                        f.write(f"│   ├── {series}/\n")
            f.write("├── Logs/\n")
            f.write("├── Reports/\n")
            f.write("└── MASTER_INDEX.md\n")
            f.write("```\n")
        
        print(f"Master index created: {master_index_file}")
    
    def validate_organization(self) -> Dict:
        """Validate the organization and identify issues."""
        print("Validating content organization...")
        
        validation_report = {
            'total_files_checked': 0,
            'properly_organized': 0,
            'misplaced_files': [],
            'empty_directories': [],
            'duplicate_files': [],
            'corrupted_files': [],
            'validation_date': datetime.now().isoformat()
        }
        
        # Check for empty directories
        for tractate_dir in self.base_dir.iterdir():
            if tractate_dir.is_dir() and tractate_dir.name not in ['Logs', 'Reports']:
                for series_dir in tractate_dir.iterdir():
                    if series_dir.is_dir():
                        files = list(series_dir.glob('*'))
                        if not files:
                            validation_report['empty_directories'].append(str(series_dir.relative_to(self.base_dir)))
        
        # Check file organization
        file_hashes = {}
        for file_path in self.base_dir.rglob('*.txt'):
            validation_report['total_files_checked'] += 1
            
            try:
                # Check if file is in correct location
                title = self.extract_title_from_file(file_path)
                expected_tractate, expected_series = self.classify_content(title)
                
                current_path_parts = file_path.parts
                if len(current_path_parts) >= 3:
                    current_tractate = current_path_parts[-3]
                    current_series = current_path_parts[-2]
                    
                    if current_tractate == expected_tractate and current_series == expected_series:
                        validation_report['properly_organized'] += 1
                    else:
                        validation_report['misplaced_files'].append({
                            'file': str(file_path.relative_to(self.base_dir)),
                            'current_location': f"{current_tractate}/{current_series}",
                            'suggested_location': f"{expected_tractate}/{expected_series}"
                        })
                
                # Check for duplicates (simple hash check)
                file_size = file_path.stat().st_size
                file_key = f"{file_path.name}_{file_size}"
                if file_key in file_hashes:
                    validation_report['duplicate_files'].append({
                        'file1': str(file_hashes[file_key].relative_to(self.base_dir)),
                        'file2': str(file_path.relative_to(self.base_dir))
                    })
                else:
                    file_hashes[file_key] = file_path
                
            except Exception as e:
                validation_report['corrupted_files'].append({
                    'file': str(file_path.relative_to(self.base_dir)),
                    'error': str(e)
                })
        
        return validation_report
    
    def save_reports(self, output_dir: str = None):
        """Save all organization reports."""
        if output_dir:
            reports_dir = Path(output_dir)
        else:
            reports_dir = self.base_dir / "Reports"
        
        reports_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save inventory
        inventory = self.generate_content_inventory()
        with open(reports_dir / f"content_inventory_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(inventory, f, indent=2, ensure_ascii=False)
        
        # Save validation report
        validation = self.validate_organization()
        with open(reports_dir / f"validation_report_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(validation, f, indent=2, ensure_ascii=False)
        
        # Save summary report
        with open(reports_dir / f"organization_summary_{timestamp}.txt", 'w', encoding='utf-8') as f:
            f.write("CONTENT ORGANIZATION SUMMARY\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Base Directory: {self.base_dir}\n\n")
            
            f.write("INVENTORY SUMMARY:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total Files: {inventory['total_files']}\n")
            f.write(f"Total Size: {inventory['size_stats'].get('total_size_mb', 0):.1f} MB\n")
            f.write(f"Tractates: {len(inventory['tractates'])}\n\n")
            
            f.write("VALIDATION SUMMARY:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Files Checked: {validation['total_files_checked']}\n")
            f.write(f"Properly Organized: {validation['properly_organized']}\n")
            f.write(f"Misplaced Files: {len(validation['misplaced_files'])}\n")
            f.write(f"Empty Directories: {len(validation['empty_directories'])}\n")
            f.write(f"Duplicate Files: {len(validation['duplicate_files'])}\n")
            f.write(f"Corrupted Files: {len(validation['corrupted_files'])}\n")
        
        print(f"Reports saved to: {reports_dir}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Organize Mercaz Daf Yomi transcript content")
    parser.add_argument('--base-dir', default='Mercaz_Daf_Yomi_Transcripts', 
                       help='Base directory for transcripts')
    parser.add_argument('--source-dir', help='Source directory to organize from')
    parser.add_argument('--create-structure', action='store_true', 
                       help='Create directory structure')
    parser.add_argument('--organize-files', action='store_true', 
                       help='Organize existing files')
    parser.add_argument('--create-indexes', action='store_true', 
                       help='Create tractate indexes')
    parser.add_argument('--generate-reports', action='store_true', 
                       help='Generate organization reports')
    parser.add_argument('--all', action='store_true', 
                       help='Run all organization tasks')
    
    args = parser.parse_args()
    
    try:
        organizer = ContentOrganizer(args.base_dir)
        
        if args.all or args.create_structure:
            organizer.create_directory_structure()
        
        if args.all or args.organize_files:
            organizer.organize_existing_files(args.source_dir)
        
        if args.all or args.create_indexes:
            organizer.create_tractate_indexes()
            organizer.generate_master_index()
        
        if args.all or args.generate_reports:
            organizer.save_reports()
        
        print("Content organization completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()