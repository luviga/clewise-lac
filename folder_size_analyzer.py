# -*- coding: utf-8 -*-
"""
Folder Size Analyzer for MODELS_LAC
===================================
Procedural script to identify disk space usage per folder.
Helps decide what to erase to make the project lighter.

Author: Luis Victor / CLG
Usage: Update ROOT_PATH and run in Spyder
"""

import os
from pathlib import Path
from collections import defaultdict


# =============================================================================
# CONFIGURATION - UPDATE THESE PATHS
# =============================================================================
ROOT_PATH = r"C:\Users\luisfernando\Dropbox\2_WORK\MODELS_LAC_2"
OUTPUT_PATH = r"C:\Users\luisfernando\Dropbox\2_WORK\MODELS_LAC_2"


# =============================================================================
# STEP 1: UTILITY FUNCTIONS
# =============================================================================

def get_folder_size_bytes(folder_path):
    """Calculate total size of a folder in bytes."""
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total += os.path.getsize(filepath)
                except (OSError, FileNotFoundError):
                    pass  # Skip files that can't be accessed
    except (OSError, PermissionError):
        pass
    return total


def bytes_to_human_readable(size_bytes):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def bytes_to_gb(size_bytes):
    """Convert bytes to GB (float)."""
    return size_bytes / (1024 ** 3)


# =============================================================================
# STEP 2: ANALYZE TOP-LEVEL FOLDERS (Countries)
# =============================================================================

def analyze_country_folders(root_path):
    """Analyze disk usage by country folder."""
    print("\n" + "=" * 70)
    print("STEP 2: COUNTRY-LEVEL ANALYSIS")
    print("=" * 70)
    
    country_sizes = []
    
    for item in os.listdir(root_path):
        item_path = os.path.join(root_path, item)
        if os.path.isdir(item_path):
            size = get_folder_size_bytes(item_path)
            country_sizes.append((item, size))
    
    # Sort by size descending
    country_sizes.sort(key=lambda x: x[1], reverse=True)
    
    total_size = sum(s[1] for s in country_sizes)
    
    print(f"\nTotal MODELS_LAC size: {bytes_to_human_readable(total_size)}")
    print("-" * 70)
    print(f"{'Country':<30} {'Size':>15} {'% of Total':>12}")
    print("-" * 70)
    
    for name, size in country_sizes:
        pct = (size / total_size * 100) if total_size > 0 else 0
        print(f"{name:<30} {bytes_to_human_readable(size):>15} {pct:>10.1f}%")
    
    return country_sizes, total_size


# =============================================================================
# STEP 3: ANALYZE MODEL FOLDERS WITHIN COUNTRIES
# =============================================================================

def analyze_model_folders(root_path):
    """Analyze disk usage by model folder (second level)."""
    print("\n" + "=" * 70)
    print("STEP 3: MODEL-LEVEL ANALYSIS (All models sorted by size)")
    print("=" * 70)
    
    model_sizes = []
    
    for country in os.listdir(root_path):
        country_path = os.path.join(root_path, country)
        if not os.path.isdir(country_path):
            continue
            
        for model in os.listdir(country_path):
            model_path = os.path.join(country_path, model)
            if os.path.isdir(model_path):
                size = get_folder_size_bytes(model_path)
                model_sizes.append((country, model, size, model_path))
    
    # Sort by size descending
    model_sizes.sort(key=lambda x: x[2], reverse=True)
    
    print(f"\n{'Country':<20} {'Model':<40} {'Size':>15}")
    print("-" * 80)
    
    for country, model, size, path in model_sizes[:30]:  # Top 30
        print(f"{country:<20} {model:<40} {bytes_to_human_readable(size):>15}")
    
    if len(model_sizes) > 30:
        print(f"\n... and {len(model_sizes) - 30} more models (smaller)")
    
    return model_sizes


# =============================================================================
# STEP 4: ANALYZE SUBFOLDER TYPES (Executables, Outputs, etc.)
# =============================================================================

def analyze_subfolder_types(root_path):
    """Identify which subfolder types consume the most space."""
    print("\n" + "=" * 70)
    print("STEP 4: SUBFOLDER TYPE ANALYSIS")
    print("(Which types of folders are taking up space?)")
    print("=" * 70)
    
    # Common OSeMOSYS subfolder patterns
    patterns = {
        'Executables': 0,
        'A1_Outputs': 0,
        'A2_Output_Params': 0,
        'B1_Output_Params': 0,
        'A1_Inputs': 0,
        'A2_Extra_Inputs': 0,
        'BackUp': 0,
        'backup': 0,
        'reference_': 0,  # Any folder starting with reference_
        'tests_results': 0,
        'EXP': 0,
        'config': 0,
        'Other': 0
    }
    
    pattern_folders = defaultdict(list)  # Track which folders match each pattern
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        folder_name = os.path.basename(dirpath)
        rel_path = os.path.relpath(dirpath, root_path)
        
        # Calculate direct size (files in this folder only, not subdirs)
        direct_size = sum(
            os.path.getsize(os.path.join(dirpath, f))
            for f in filenames
            if os.path.exists(os.path.join(dirpath, f))
        )
        
        if direct_size == 0:
            continue
        
        # Match patterns
        matched = False
        for pattern in patterns:
            if pattern == 'Other':
                continue
            if pattern == 'reference_':
                if folder_name.startswith('reference_'):
                    patterns[pattern] += direct_size
                    pattern_folders[pattern].append((rel_path, direct_size))
                    matched = True
                    break
            elif folder_name == pattern or folder_name.lower() == pattern.lower():
                patterns[pattern] += direct_size
                pattern_folders[pattern].append((rel_path, direct_size))
                matched = True
                break
        
        if not matched:
            patterns['Other'] += direct_size
    
    # Sort and display
    sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
    total = sum(p[1] for p in sorted_patterns)
    
    print(f"\n{'Folder Type':<25} {'Size':>15} {'% of Total':>12}")
    print("-" * 55)
    
    for pattern, size in sorted_patterns:
        if size > 0:
            pct = (size / total * 100) if total > 0 else 0
            print(f"{pattern:<25} {bytes_to_human_readable(size):>15} {pct:>10.1f}%")
    
    return patterns, pattern_folders


# =============================================================================
# STEP 5: ANALYZE FILE TYPES
# =============================================================================

def analyze_file_types(root_path):
    """Analyze disk usage by file extension."""
    print("\n" + "=" * 70)
    print("STEP 5: FILE TYPE ANALYSIS")
    print("(Which file extensions are consuming space?)")
    print("=" * 70)
    
    extension_sizes = defaultdict(int)
    extension_counts = defaultdict(int)
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                size = os.path.getsize(filepath)
                ext = os.path.splitext(filename)[1].lower()
                if not ext:
                    ext = '(no extension)'
                extension_sizes[ext] += size
                extension_counts[ext] += 1
            except (OSError, FileNotFoundError):
                pass
    
    # Sort by size descending
    sorted_extensions = sorted(extension_sizes.items(), key=lambda x: x[1], reverse=True)
    total = sum(e[1] for e in sorted_extensions)
    
    print(f"\n{'Extension':<15} {'Count':>10} {'Size':>15} {'% of Total':>12}")
    print("-" * 55)
    
    for ext, size in sorted_extensions[:20]:  # Top 20
        count = extension_counts[ext]
        pct = (size / total * 100) if total > 0 else 0
        print(f"{ext:<15} {count:>10} {bytes_to_human_readable(size):>15} {pct:>10.1f}%")
    
    return extension_sizes


# =============================================================================
# STEP 6: FIND LARGEST INDIVIDUAL FOLDERS
# =============================================================================

def find_largest_folders(root_path, top_n=30):
    """Find the N largest individual folders."""
    print("\n" + "=" * 70)
    print(f"STEP 6: TOP {top_n} LARGEST FOLDERS")
    print("(Direct candidates for cleanup)")
    print("=" * 70)
    
    folder_sizes = []
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Calculate direct size (files in this folder only)
        direct_size = 0
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                direct_size += os.path.getsize(filepath)
            except (OSError, FileNotFoundError):
                pass
        
        if direct_size > 0:
            rel_path = os.path.relpath(dirpath, root_path)
            folder_sizes.append((rel_path, direct_size))
    
    # Sort by size descending
    folder_sizes.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n{'Folder Path':<65} {'Size':>12}")
    print("-" * 80)
    
    for path, size in folder_sizes[:top_n]:
        # Truncate path if too long
        display_path = path if len(path) <= 63 else "..." + path[-60:]
        print(f"{display_path:<65} {bytes_to_human_readable(size):>12}")
    
    return folder_sizes


# =============================================================================
# STEP 7: IDENTIFY CLEANUP CANDIDATES
# =============================================================================

def identify_cleanup_candidates(root_path, model_sizes, pattern_folders):
    """Suggest folders that are safe to delete or archive."""
    print("\n" + "=" * 70)
    print("STEP 7: CLEANUP RECOMMENDATIONS")
    print("=" * 70)
    
    recommendations = []
    
    # Check for backup folders
    print("\n[A] BACKUP FOLDERS (usually safe to delete):")
    print("-" * 50)
    backup_total = 0
    for dirpath, dirnames, filenames in os.walk(root_path):
        folder_name = os.path.basename(dirpath).lower()
        if folder_name in ['backup', 'bkp', 'bak'] or 'backup' in folder_name.lower():
            size = get_folder_size_bytes(dirpath)
            if size > 0:
                rel_path = os.path.relpath(dirpath, root_path)
                print(f"  {rel_path}: {bytes_to_human_readable(size)}")
                backup_total += size
    print(f"  TOTAL: {bytes_to_human_readable(backup_total)}")
    
    # Check for reference folders
    print("\n[B] REFERENCE/ARCHIVE FOLDERS (review before deleting):")
    print("-" * 50)
    ref_total = 0
    for dirpath, dirnames, filenames in os.walk(root_path):
        folder_name = os.path.basename(dirpath).lower()
        if folder_name.startswith('reference_') or 'previous' in folder_name:
            size = get_folder_size_bytes(dirpath)
            if size > 0:
                rel_path = os.path.relpath(dirpath, root_path)
                print(f"  {rel_path}: {bytes_to_human_readable(size)}")
                ref_total += size
    print(f"  TOTAL: {bytes_to_human_readable(ref_total)}")
    
    # Check for Executables folders (often can be regenerated)
    print("\n[C] EXECUTABLES FOLDERS (can usually be regenerated):")
    print("-" * 50)
    exec_total = 0
    for dirpath, dirnames, filenames in os.walk(root_path):
        if os.path.basename(dirpath) == 'Executables':
            size = get_folder_size_bytes(dirpath)
            if size > 0:
                rel_path = os.path.relpath(dirpath, root_path)
                print(f"  {rel_path}: {bytes_to_human_readable(size)}")
                exec_total += size
    print(f"  TOTAL: {bytes_to_human_readable(exec_total)}")
    
    # Check for test results
    print("\n[D] TEST RESULTS (usually safe to delete):")
    print("-" * 50)
    test_total = 0
    for dirpath, dirnames, filenames in os.walk(root_path):
        if os.path.basename(dirpath) == 'tests_results':
            size = get_folder_size_bytes(dirpath)
            if size > 0:
                rel_path = os.path.relpath(dirpath, root_path)
                print(f"  {rel_path}: {bytes_to_human_readable(size)}")
                test_total += size
    print(f"  TOTAL: {bytes_to_human_readable(test_total)}")
    
    # Summary
    print("\n" + "=" * 70)
    print("CLEANUP SUMMARY")
    print("=" * 70)
    total_recoverable = backup_total + ref_total + exec_total + test_total
    print(f"""
Potential space recovery:
  - Backup folders:     {bytes_to_human_readable(backup_total)}
  - Reference folders:  {bytes_to_human_readable(ref_total)}
  - Executables:        {bytes_to_human_readable(exec_total)}
  - Test results:       {bytes_to_human_readable(test_total)}
  ----------------------------------------
  TOTAL POTENTIAL:      {bytes_to_human_readable(total_recoverable)}
    """)
    
    return {
        'backup': backup_total,
        'reference': ref_total,
        'executables': exec_total,
        'tests': test_total,
        'total': total_recoverable
    }


# =============================================================================
# STEP 8: EXPORT RESULTS TO CSV
# =============================================================================

def export_to_csv(root_path, folder_sizes, output_file='folder_analysis.csv'):
    """Export detailed folder analysis to CSV for further review."""
    import csv
    
    output_path = os.path.join(OUTPUT_PATH, output_file)
    
    print(f"\n[EXPORT] Writing detailed analysis to: {output_path}")
    
    all_folders = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        size = get_folder_size_bytes(dirpath)
        rel_path = os.path.relpath(dirpath, root_path)
        depth = rel_path.count(os.sep)
        folder_name = os.path.basename(dirpath)
        
        # Classify folder type
        folder_type = 'Other'
        if folder_name == 'Executables':
            folder_type = 'Executables'
        elif folder_name.startswith('A1_'):
            folder_type = 'A1_Stage'
        elif folder_name.startswith('A2_'):
            folder_type = 'A2_Stage'
        elif folder_name.startswith('B1_'):
            folder_type = 'B1_Stage'
        elif 'backup' in folder_name.lower():
            folder_type = 'Backup'
        elif folder_name.startswith('reference_'):
            folder_type = 'Reference'
        elif folder_name == 'tests_results':
            folder_type = 'Tests'
        
        all_folders.append({
            'path': rel_path,
            'folder_name': folder_name,
            'depth': depth,
            'size_bytes': size,
            'size_readable': bytes_to_human_readable(size),
            'size_gb': round(bytes_to_gb(size), 4),
            'type': folder_type
        })
    
    # Sort by size
    all_folders.sort(key=lambda x: x['size_bytes'], reverse=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['path', 'folder_name', 'depth', 
                                                'size_bytes', 'size_readable', 
                                                'size_gb', 'type'])
        writer.writeheader()
        writer.writerows(all_folders)
    
    print(f"  Exported {len(all_folders)} folders to CSV")
    return output_path


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main execution pipeline."""
    print("=" * 70)
    print("FOLDER SIZE ANALYZER FOR MODELS_LAC")
    print("=" * 70)
    print(f"\nAnalyzing: {ROOT_PATH}")
    
    # Verify path exists
    if not os.path.exists(ROOT_PATH):
        print(f"\nERROR: Path does not exist: {ROOT_PATH}")
        print("Please update ROOT_PATH in the configuration section.")
        return
    
    # Run analysis pipeline
    print("\nStarting analysis... (this may take a few minutes)")
    
    # Step 2: Country-level
    country_sizes, total_size = analyze_country_folders(ROOT_PATH)
    
    # Step 3: Model-level
    model_sizes = analyze_model_folders(ROOT_PATH)
    
    # Step 4: Subfolder types
    patterns, pattern_folders = analyze_subfolder_types(ROOT_PATH)
    
    # Step 5: File types
    extension_sizes = analyze_file_types(ROOT_PATH)
    
    # Step 6: Largest folders
    folder_sizes = find_largest_folders(ROOT_PATH)
    
    # Step 7: Cleanup recommendations
    cleanup = identify_cleanup_candidates(ROOT_PATH, model_sizes, pattern_folders)
    
    # Step 8: Export to CSV
    csv_path = export_to_csv(ROOT_PATH, folder_sizes)
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"""
Next steps:
1. Review the CSV file for detailed folder-by-folder breakdown
2. Consider deleting backup folders (Category A) first
3. Archive or delete old reference folders (Category B)
4. Executables can be regenerated if needed (Category C)
5. Test results are usually safe to delete (Category D)

CSV exported to: {csv_path}
    """)


if __name__ == "__main__":
    main()