# cleanup_old_files.py
"""
Cleanup script to remove unnecessary files from old system
"""
import os
import shutil

# Files to delete (old documentation and test files)
FILES_TO_DELETE = [
    'ADK_API_KEY_SOLUTION.md',
    'ADK_FIX.md',
    'DOCKER_BUILD_SUCCESS.md',
    'DOCKER_GUIDE.md',
    'Dockerfile.adk',
    'Dockerfile.dashboard',
    'Dockerfile.mcp',
    'docker-compose.yml',
    'FIXES_SUMMARY.md',
    'TEST_RESULTS.md',
    'agent.py',  # Old agent file
    'check_db.py',
    'debug_db.py',
    'debug_mcp.py',
    'run_migration.py',
    'test_ai_integration.py',
    'test_api.py',
    'test_enhanced_platform.py',
    'test_interview_platform.py',
    'test_leetcode_stats.py',
    'backend.log',
    'mcp.log',
    'roadmap_debug.log',
    'mcp_cap.txt',
    '.evn',  # Typo file
    'start_adk.bat',
    'start_all.bat',
]

# Directories to delete (old/unused)
DIRS_TO_DELETE = [
    'Maang_Tracker',  # Duplicate/old directory
]

def cleanup():
    """Remove unnecessary files and directories"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    deleted_files = []
    deleted_dirs = []
    errors = []
    
    # Delete files
    for file in FILES_TO_DELETE:
        file_path = os.path.join(base_dir, file)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                deleted_files.append(file)
                print(f"✓ Deleted: {file}")
            except Exception as e:
                errors.append(f"Error deleting {file}: {e}")
                print(f"✗ Error deleting {file}: {e}")
    
    # Delete directories
    for dir_name in DIRS_TO_DELETE:
        dir_path = os.path.join(base_dir, dir_name)
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                deleted_dirs.append(dir_name)
                print(f"✓ Deleted directory: {dir_name}")
            except Exception as e:
                errors.append(f"Error deleting {dir_name}: {e}")
                print(f"✗ Error deleting directory {dir_name}: {e}")
    
    # Summary
    print("\n" + "="*50)
    print("CLEANUP SUMMARY")
    print("="*50)
    print(f"Files deleted: {len(deleted_files)}")
    print(f"Directories deleted: {len(deleted_dirs)}")
    print(f"Errors: {len(errors)}")
    
    if errors:
        print("\nErrors encountered:")
        for error in errors:
            print(f"  - {error}")
    
    print("\n✓ Cleanup complete!")

if __name__ == "__main__":
    cleanup()
