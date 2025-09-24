#!/usr/bin/env python3
"""
Cleanup script to remove pickle files after migrating to ChromaDB-only storage.
This script removes all .pkl files from the chroma_db directory.
"""

import os
import glob

def cleanup_pickle_files():
    """Remove all pickle files from the ChromaDB directory"""
    chroma_db_path = "./chroma_db"
    
    if not os.path.exists(chroma_db_path):
        print(f"ChromaDB directory '{chroma_db_path}' not found. Nothing to clean up.")
        return
    
    # Find all .pkl files in the ChromaDB directory
    pickle_files = glob.glob(os.path.join(chroma_db_path, "*.pkl"))
    
    if not pickle_files:
        print("No pickle files found. Clean up not needed.")
        return
    
    print(f"Found {len(pickle_files)} pickle files to remove:")
    for file_path in pickle_files:
        print(f"  - {os.path.basename(file_path)}")
    
    # Ask for confirmation
    response = input("\nDo you want to remove these files? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        removed_count = 0
        for file_path in pickle_files:
            try:
                os.remove(file_path)
                print(f"✅ Removed {os.path.basename(file_path)}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Error removing {os.path.basename(file_path)}: {e}")
        
        print(f"\n🎉 Successfully removed {removed_count} out of {len(pickle_files)} pickle files.")
        print("ChromaDB migration to ChromaDB-only storage is complete!")
    else:
        print("Cleanup cancelled. Pickle files remain.")

if __name__ == "__main__":
    print("🧹 Maxwell RAG - Pickle Files Cleanup")
    print("=" * 45)
    print("This script removes pickle files after migrating to ChromaDB-only storage.")
    print("All document data is now stored directly in ChromaDB.\n")
    
    cleanup_pickle_files() 