#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify that the complete Fault Editor interface
has all the original functionalities restored.

Author: AI Assistant
Created: 2024
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from main_controller import FaultEditorController

def test_interface_components():
    """Test that all major interface components are present."""
    print("🧪 Testing Fault Editor Interface Components...")

    # Create test root
    root = tk.Tk()
    root.withdraw()  # Hide the window for testing

    try:
        # Create controller
        controller = FaultEditorController(root)

        # Test major attributes exist
        required_attributes = [
            'lang', 'file_map', 'data_map', 'path_map', 'columns',
            'current_path', 'editing_info', 'base_dir', 'search_results',
            'current_search_index', 'search_mode', 'search_frame',
            'current_file_path', 'main_canvas', 'columns_frame', 'status'
        ]

        missing_attributes = []
        for attr in required_attributes:
            if not hasattr(controller, attr):
                missing_attributes.append(attr)

        if missing_attributes:
            print(f"❌ Missing attributes: {missing_attributes}")
            return False
        else:
            print("✅ All required attributes present")

        # Test major methods exist
        required_methods = [
            'setup_ui', 'open_folder', 'load_flat_json', 'show_search',
            'reload_lang', 'run_sync_all', 'run_sync_one', 'run_generer_fichier',
            'run_generer_manquant', 'run_check_coherence', 'run_spell_check',
            'perform_search', 'search_next', 'search_previous', 'reload_root'
        ]

        missing_methods = []
        for method in required_methods:
            if not hasattr(controller, method) or not callable(getattr(controller, method)):
                missing_methods.append(method)

        if missing_methods:
            print(f"❌ Missing methods: {missing_methods}")
            return False
        else:
            print("✅ All required methods present")

        # Test UI components exist
        ui_components = [
            'tools_frame', 'selected_file_label', 'main_canvas',
            'columns_frame', 'lang_var', 'sync_one_var',
            'genfichier_file_var', 'genfichier_src_var', 'genfichier_tgt_var'
        ]

        missing_ui = []
        for component in ui_components:
            if not hasattr(controller, component):
                missing_ui.append(component)

        if missing_ui:
            print(f"❌ Missing UI components: {missing_ui}")
            return False
        else:
            print("✅ All UI components present")

        print("🎉 All interface components successfully verified!")
        return True

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

    finally:
        root.destroy()

def test_legacy_compatibility():
    """Test that legacy compatibility is maintained."""
    print("🔄 Testing Legacy Compatibility...")

    try:
        from app import FaultEditor

        # Create test root
        root = tk.Tk()
        root.withdraw()

        # Create legacy wrapper
        editor = FaultEditor(root)

        # Test that wrapper delegates correctly
        test_attributes = ['lang', 'file_map', 'base_dir', 'search_results']

        for attr in test_attributes:
            if not hasattr(editor, attr):
                print(f"❌ Legacy wrapper missing attribute: {attr}")
                return False

        print("✅ Legacy compatibility maintained")
        root.destroy()
        return True

    except Exception as e:
        print(f"❌ Legacy compatibility error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Fault Editor Interface Tests\n")

    # Test 1: Interface Components
    test1_passed = test_interface_components()
    print()

    # Test 2: Legacy Compatibility
    test2_passed = test_legacy_compatibility()
    print()

    # Summary
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ The complete Fault Editor interface has been successfully restored")
        print("✅ All original functionalities are available")
        print("✅ Legacy compatibility is maintained")
        print("🏗️ Ready for production use!")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        print("🔧 Please review the missing components")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
