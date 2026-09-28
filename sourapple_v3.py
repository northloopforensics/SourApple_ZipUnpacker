#!/usr/bin/env python3
"""
SourApple V3 - Advanced Recursive Zip File Unpacker
Improved version with CustomTkinter GUI, comprehensive logging, and enhanced features
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from zipfile import ZipFile, BadZipFile
import os
import threading
import time
import sys
from datetime import datetime
from pathlib import Path
import shutil

# Increase recursion limit to handle very deep nested zip files
# Default is 1000, setting to 10000 to handle 1000+ nested levels safely
sys.setrecursionlimit(10000)


class ZipUnpackerApp:
    def __init__(self):
        # Configure CustomTkinter appearance
        ctk.set_appearance_mode("system")  # Modes: system (default), light, dark
        ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
        
        self.root = ctk.CTk()
        self.root.title("SourApple V3 - Recursive Zip Unpacker")
        self.root.geometry("400x900")
        self.root.minsize(900, 400)
        
        # Initialize variables
        self.input_path = ctk.StringVar()
        self.output_path = ctk.StringVar()
        self.is_processing = False
        self.processed_files = []
        self.copied_files = []
        self.error_log = []
        self.start_time = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the user interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="SourApple V3 - Recursive Zip Unpacker",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Input selection frame
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(
            input_frame, 
            text="Input (Folder or Zip File):",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 5))
        
        input_selection_frame = ctk.CTkFrame(input_frame)
        input_selection_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.input_entry = ctk.CTkEntry(
            input_selection_frame,
            textvariable=self.input_path,
            placeholder_text="Select input folder or zip file...",
            height=35
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        ctk.CTkButton(
            input_selection_frame,
            text="Browse Folder",
            command=self.select_input_folder,
            width=120,
            height=35
        ).pack(side="right", padx=(5, 5), pady=10)
        
        ctk.CTkButton(
            input_selection_frame,
            text="Browse Zip",
            command=self.select_input_zip,
            width=120,
            height=35
        ).pack(side="right", padx=(0, 5), pady=10)
        
        # Output selection frame
        output_frame = ctk.CTkFrame(main_frame)
        output_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(
            output_frame, 
            text="Output Location:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 5))
        
        output_selection_frame = ctk.CTkFrame(output_frame)
        output_selection_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.output_entry = ctk.CTkEntry(
            output_selection_frame,
            textvariable=self.output_path,
            placeholder_text="Select output folder...",
            height=35
        )
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        ctk.CTkButton(
            output_selection_frame,
            text="Browse",
            command=self.select_output_folder,
            width=120,
            height=35
        ).pack(side="right", padx=(0, 10), pady=10)
        
        # Progress and status frame
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(
            progress_frame, 
            text="Progress & Status:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 5))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to process files...",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(anchor="w", padx=20, pady=(0, 15))
        
        # Log text area
        log_frame = ctk.CTkFrame(main_frame)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        ctk.CTkLabel(
            log_frame, 
            text="Activity Log:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 5))
        
        self.log_text = ctk.CTkTextbox(log_frame, height=150)
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Control buttons frame
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.start_button = ctk.CTkButton(
            button_frame,
            text="Start Unpacking",
            command=self.start_unpacking,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.start_button.pack(side="left", padx=(20, 10), pady=15)
        
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="Stop",
            command=self.stop_processing,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color="red",
            hover_color="darkred",
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=(0, 10), pady=15)
        
        ctk.CTkButton(
            button_frame,
            text="Clear Log",
            command=self.clear_log,
            height=40
        ).pack(side="left", padx=(0, 10), pady=15)
        
        ctk.CTkButton(
            button_frame,
            text="Save Report",
            command=self.save_report,
            height=40
        ).pack(side="left", padx=(0, 10), pady=15)
        
        ctk.CTkButton(
            button_frame,
            text="Help",
            command=self.show_help,
            height=40
        ).pack(side="right", padx=(0, 20), pady=15)
    
    def select_input_folder(self):
        """Select input folder"""
        folder_path = filedialog.askdirectory(title="Select Input Folder")
        if folder_path:
            self.input_path.set(folder_path)
            self.log_message(f"Input folder selected: {folder_path}")
    
    def select_input_zip(self):
        """Select input zip file"""
        file_path = filedialog.askopenfilename(
            title="Select Zip File",
            filetypes=[("Zip files", "*.zip"), ("All files", "*.*")]
        )
        if file_path:
            self.input_path.set(file_path)
            self.log_message(f"Input zip file selected: {file_path}")
    
    def select_output_folder(self):
        """Select output folder"""
        folder_path = filedialog.askdirectory(title="Select Output Folder")
        if folder_path:
            self.output_path.set(folder_path)
            self.log_message(f"Output folder selected: {folder_path}")
    
    def log_message(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.log_text.insert("end", formatted_message)
        self.log_text.see("end")
        self.root.update_idletasks()
    
    def clear_log(self):
        """Clear the log text area"""
        self.log_text.delete("1.0", "end")
    
    def start_unpacking(self):
        """Start the unpacking process"""
        if not self.input_path.get():
            messagebox.showerror("Error", "Please select an input folder or zip file.")
            return
        
        if not self.output_path.get():
            messagebox.showerror("Error", "Please select an output folder.")
            return
        
        if not os.path.exists(self.input_path.get()):
            messagebox.showerror("Error", "Input path does not exist.")
            return
        
        if not os.path.exists(self.output_path.get()):
            messagebox.showerror("Error", "Output folder does not exist.")
            return
        
        # Start processing in a separate thread to prevent UI freezing
        self.is_processing = True
        self.processed_files = []
        self.copied_files = []
        self.error_log = []
        self.start_time = datetime.now()
        
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        
        self.log_message("Starting unpacking process...")
        
        processing_thread = threading.Thread(target=self.process_files)
        processing_thread.daemon = True
        processing_thread.start()
    
    def stop_processing(self):
        """Stop the processing"""
        self.is_processing = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.log_message("Processing stopped by user.")
        self.update_status("Processing stopped.")
    
    def process_files(self):
        """Main processing function"""
        try:
            input_path = self.input_path.get()
            
            if os.path.isfile(input_path) and input_path.lower().endswith('.zip'):
                # Single zip file processing
                self.log_message(f"Processing single zip file: {os.path.basename(input_path)}")
                self.process_single_zip(input_path)
            elif os.path.isdir(input_path):
                # Folder processing
                self.log_message(f"Processing folder: {input_path}")
                self.process_folder(input_path)
            else:
                self.log_message("Error: Invalid input path or unsupported file type.")
                return
            
            self.finish_processing()
            
        except Exception as e:
            self.log_message(f"Critical error during processing: {str(e)}")
            self.error_log.append(f"Critical error: {str(e)}")
        finally:
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
    
    def process_folder(self, folder_path):
        """Process all files and folders, extracting zips and copying regular content"""
        try:
            # Collect all items to process
            zip_files = []
            other_items = []
            
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file.lower().endswith('.zip'):
                        zip_files.append(file_path)
                    else:
                        # Only add non-zip files to other_items
                        other_items.append(file_path)
                
                # Also collect directories for copying
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    other_items.append(dir_path)
            
            total_items = len(zip_files) + len(other_items)
            
            if total_items == 0:
                self.log_message("No files found in the selected folder.")
                self.update_status("No files found.")
                return
            
            self.log_message(f"Found {len(zip_files)} zip file(s) and {len(other_items)} other item(s) to process.")
            
            processed_count = 0
            
            # First, copy all non-zip files and create directory structure
            if other_items:
                self.log_message("Copying non-archive files and creating directory structure...")
                for item_path in other_items:
                    if not self.is_processing:
                        break
                    
                    processed_count += 1
                    relative_path = os.path.relpath(item_path, folder_path)
                    output_path = os.path.join(self.output_path.get(), relative_path)
                    
                    self.update_status(f"Copying {processed_count}/{total_items}: {os.path.basename(item_path)}")
                    self.progress_bar.set(processed_count / total_items)
                    
                    try:
                        if os.path.isfile(item_path):
                            # Copy file (excluding zip files)
                            os.makedirs(os.path.dirname(output_path), exist_ok=True)
                            shutil.copy2(item_path, output_path)
                            self.log_message(f"  Copied file: {relative_path}")
                            self.copied_files.append({
                                'source': item_path,
                                'destination': output_path,
                                'type': 'file',
                                'timestamp': datetime.now()
                            })
                        elif os.path.isdir(item_path):
                            # Create directory
                            os.makedirs(output_path, exist_ok=True)
                            self.log_message(f"  Created directory: {relative_path}")
                            self.copied_files.append({
                                'source': item_path,
                                'destination': output_path,
                                'type': 'directory',
                                'timestamp': datetime.now()
                            })
                    except Exception as e:
                        error_msg = f"Error copying {relative_path}: {str(e)}"
                        self.log_message(error_msg)
                        self.error_log.append(error_msg)
            
            # Then process zip files
            if zip_files:
                self.log_message("Processing zip archives...")
                for i, zip_file in enumerate(zip_files):
                    if not self.is_processing:
                        break
                    
                    processed_count += 1
                    self.update_status(f"Extracting {processed_count}/{total_items}: {os.path.basename(zip_file)}")
                    self.progress_bar.set(processed_count / total_items)
                    
                    # Calculate relative path to maintain folder structure
                    relative_path = os.path.relpath(zip_file, folder_path)
                    output_dir = os.path.join(self.output_path.get(), os.path.dirname(relative_path))
                    
                    self.process_single_zip(zip_file, output_dir)
                
        except Exception as e:
            self.log_message(f"Error processing folder: {str(e)}")
            self.error_log.append(f"Folder processing error: {str(e)}")
    
    def process_single_zip(self, zip_path, custom_output_dir=None):
        """Process a single zip file recursively"""
        try:
            if custom_output_dir:
                base_output_dir = custom_output_dir
            else:
                base_output_dir = self.output_path.get()
            
            # Create output directory structure
            zip_name = os.path.splitext(os.path.basename(zip_path))[0]
            extract_dir = os.path.join(base_output_dir, zip_name)
            
            self.log_message(f"Extracting: {os.path.basename(zip_path)}")
            self.unpack_zip_recursive(zip_path, extract_dir, depth=0)
            
        except Exception as e:
            error_msg = f"Error processing {os.path.basename(zip_path)}: {str(e)}"
            self.log_message(error_msg)
            self.error_log.append(error_msg)
    
    def unpack_zip_recursive(self, zip_path, extract_path, depth=0):
        """Recursively unpack zip files"""
        try:
            # Safety check for very deep recursion
            if depth > 5000:
                error_msg = f"Maximum recursion depth exceeded at {depth} levels. Stopping to prevent system issues."
                self.log_message(error_msg)
                self.error_log.append(error_msg)
                return
            
            # Warning for deep nesting
            if depth > 100 and depth % 100 == 0:
                self.log_message(f"Deep nesting detected: Currently at depth {depth}")
            
            # Create extraction directory
            os.makedirs(extract_path, exist_ok=True)
            
            # Add depth indicator to logging
            indent = "  " * min(depth + 1, 10)  # Limit indentation to keep logs readable
            if depth > 10:
                indent = f"[D{depth}] "
            
            with ZipFile(zip_path, 'r') as zip_file:
                zip_file.extractall(extract_path)
                extracted_files = zip_file.namelist()
                
                self.processed_files.append({
                    'zip_file': zip_path,
                    'extract_path': extract_path,
                    'files_count': len(extracted_files),
                    'depth': depth,
                    'timestamp': datetime.now()
                })
                
                self.log_message(f"{indent}Extracted {len(extracted_files)} file(s) to: {os.path.basename(extract_path)} (depth: {depth})")
                
                # Look for nested zip files
                nested_zips_found = 0
                for file_name in extracted_files:
                    if not self.is_processing:
                        break
                        
                    if file_name.lower().endswith('.zip'):
                        nested_zip_path = os.path.join(extract_path, file_name)
                        if os.path.exists(nested_zip_path):
                            nested_extract_path = os.path.splitext(nested_zip_path)[0]
                            nested_zips_found += 1
                            self.log_message(f"{indent}Found nested zip: {file_name} (processing at depth {depth + 1})")
                            self.unpack_zip_recursive(nested_zip_path, nested_extract_path, depth + 1)
                            
                            # Remove the nested zip file after extraction
                            try:
                                os.remove(nested_zip_path)
                                if depth < 10:  # Only log removal for shallow depths to avoid log spam
                                    self.log_message(f"{indent}Removed processed zip: {file_name}")
                            except Exception as e:
                                self.log_message(f"{indent}Warning: Could not remove {file_name}: {str(e)}")
                
                if nested_zips_found == 0 and depth < 10:
                    self.log_message(f"{indent}No nested zip files found at depth {depth}")
                
        except BadZipFile:
            error_msg = f"Skipping {os.path.basename(zip_path)} - Not a valid zip file (depth: {depth})"
            self.log_message(error_msg)
            self.error_log.append(error_msg)
        except Exception as e:
            error_msg = f"Error extracting {os.path.basename(zip_path)} at depth {depth}: {str(e)}"
            self.log_message(error_msg)
            self.error_log.append(error_msg)
    
    def update_status(self, message):
        """Update the status label"""
        self.status_label.configure(text=message)
        self.root.update_idletasks()
    
    def finish_processing(self):
        """Complete the processing and show summary"""
        if not self.is_processing:
            return
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        self.progress_bar.set(1.0)
        self.update_status("Processing completed!")
        
        # Log summary
        self.log_message("=" * 50)
        self.log_message("PROCESSING COMPLETED")
        self.log_message(f"Zip files processed: {len(self.processed_files)}")
        self.log_message(f"Files/folders copied: {len(self.copied_files)}")
        self.log_message(f"Errors encountered: {len(self.error_log)}")
        
        # Calculate maximum depth reached
        if self.processed_files:
            max_depth = max(item.get('depth', 0) for item in self.processed_files)
            avg_depth = sum(item.get('depth', 0) for item in self.processed_files) / len(self.processed_files)
            self.log_message(f"Maximum nesting depth reached: {max_depth}")
            self.log_message(f"Average nesting depth: {avg_depth:.1f}")
        
        self.log_message(f"Processing time: {duration}")
        self.log_message("=" * 50)
        
        # Include depth info in completion dialog
        depth_info = ""
        if self.processed_files:
            max_depth = max(item.get('depth', 0) for item in self.processed_files)
            depth_info = f"\nMax depth: {max_depth}"
        
        messagebox.showinfo("Complete", f"Processing completed!\n\nZip files processed: {len(self.processed_files)}\nFiles/folders copied: {len(self.copied_files)}\nErrors: {len(self.error_log)}{depth_info}\nTime: {duration}")
    
    def save_report(self):
        """Save a detailed report of the processing"""
        if not self.processed_files and not self.copied_files and not self.error_log:
            messagebox.showwarning("No Data", "No processing data to save.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Report",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("SourApple V3 - Processing Report\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Input Path: {self.input_path.get()}\n")
                    f.write(f"Output Path: {self.output_path.get()}\n")
                    f.write("\n")
                    
                    if self.start_time:
                        f.write(f"Processing Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        all_timestamps = []
                        if self.processed_files:
                            all_timestamps.extend([item['timestamp'] for item in self.processed_files])
                        if self.copied_files:
                            all_timestamps.extend([item['timestamp'] for item in self.copied_files])
                        
                        if all_timestamps:
                            last_time = max(all_timestamps)
                            duration = last_time - self.start_time
                            f.write(f"Processing Duration: {duration}\n")
                        f.write("\n")
                    
                    # Processed zip files section
                    if self.processed_files:
                        f.write("PROCESSED ZIP FILES:\n")
                        f.write("-" * 30 + "\n")
                        for item in self.processed_files:
                            f.write(f"Zip File: {item['zip_file']}\n")
                            f.write(f"Extract Path: {item['extract_path']}\n")
                            f.write(f"Files Extracted: {item['files_count']}\n")
                            f.write(f"Timestamp: {item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write("\n")
                    
                    # Copied files section
                    if self.copied_files:
                        f.write("COPIED FILES AND FOLDERS:\n")
                        f.write("-" * 30 + "\n")
                        for item in self.copied_files:
                            f.write(f"Source: {item['source']}\n")
                            f.write(f"Destination: {item['destination']}\n")
                            f.write(f"Type: {item['type']}\n")
                            f.write(f"Timestamp: {item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write("\n")
                    
                    if self.error_log:
                        f.write("ERRORS ENCOUNTERED:\n")
                        f.write("-" * 30 + "\n")
                        for error in self.error_log:
                            f.write(f"• {error}\n")
                        f.write("\n")
                    
                    f.write("ACTIVITY LOG:\n")
                    f.write("-" * 30 + "\n")
                    f.write(self.log_text.get("1.0", "end"))
                
                self.log_message(f"Report saved to: {file_path}")
                messagebox.showinfo("Success", f"Report saved successfully to:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report:\n{str(e)}")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
SourApple V3 - Recursive Zip Unpacker & File Processor

FEATURES:
• Recursively extracts nested zip archives
• Copies all non-archive files and folders
• Supports both folder and single zip file input
• User-selectable output location
• Real-time progress feedback
• Comprehensive activity logging
• Detailed processing reports

HOW TO USE:
1. Select input (folder containing files/zips or single zip file)
2. Select output folder where content will be extracted/copied
3. Click 'Start Unpacking' to begin processing
4. Monitor progress in the activity log
5. Save detailed reports when processing is complete

INPUT OPTIONS:
• Folder: Processes all content - extracts zip files and copies other files/folders
• Single Zip: Processes one zip file and any nested zips within it

OUTPUT STRUCTURE:
• Zip files are extracted to their own folders
• Regular files and folders are copied maintaining structure
• Nested zips are extracted to subfolders
• Original folder hierarchy is preserved

NOTES:
• Processing can be stopped at any time using the Stop button
• Invalid zip files are automatically skipped
• All files and folders (not just zips) are processed
• All activities are logged with timestamps
• Detailed reports can be saved for record keeping
        """
        
        help_window = ctk.CTkToplevel(self.root)
        help_window.title("SourApple V3 - Help")
        help_window.geometry("600x500")
        help_window.transient(self.root)
        help_window.grab_set()
        
        help_text_widget = ctk.CTkTextbox(help_window)
        help_text_widget.pack(fill="both", expand=True, padx=20, pady=20)
        help_text_widget.insert("1.0", help_text)
        help_text_widget.configure(state="disabled")
        
        close_button = ctk.CTkButton(
            help_window,
            text="Close",
            command=help_window.destroy
        )
        close_button.pack(pady=(0, 20))
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = ZipUnpackerApp()
    app.run()
