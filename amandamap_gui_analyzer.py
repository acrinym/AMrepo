#!/usr/bin/env python3
"""
amandamap_gui_analyzer.py — GUI application for AmandaMap analysis.
Provides interactive interface for selecting analysis options and viewing results.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
import re
import numpy as np
import pandas as pd
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

# Text processing (no TF2 required for basic analysis)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_similarity

class AmandaMapGUIAnalyzer:
    def __init__(self, root):
        """Initialize the GUI analyzer."""
        self.root = root
        self.root.title("AmandaMap Analysis Suite")
        self.root.geometry("1200x800")
        
        # Data storage
        self.entries = []
        self.chat_texts = []
        self.vectorizer = None
        self.current_analysis = None
        
        # Setup GUI
        self.setup_gui()
        
        # Auto-load data if available
        self.auto_load_data()
    
    def setup_gui(self):
        """Setup the GUI interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="AmandaMap Analysis Suite", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Control panel (left side)
        control_frame = ttk.LabelFrame(main_frame, text="Analysis Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Data loading section
        ttk.Label(control_frame, text="Data Loading:", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=(0, 10), sticky=tk.W)
        
        ttk.Button(control_frame, text="Load AmandaMap Data", 
                  command=self.load_amandamap_data).grid(row=1, column=0, pady=5, sticky=tk.W+tk.E)
        
        ttk.Button(control_frame, text="Load Chat Data", 
                  command=self.load_chat_data).grid(row=2, column=0, pady=5, sticky=tk.W+tk.E)
        
        # Analysis options section
        ttk.Label(control_frame, text="Analysis Options:", font=("Arial", 12, "bold")).grid(row=3, column=0, pady=(20, 10), sticky=tk.W)
        
        # Entry type analysis
        ttk.Button(control_frame, text="Entry Type Distribution", 
                  command=lambda: self.run_analysis("type_distribution")).grid(row=4, column=0, pady=5, sticky=tk.W+tk.E)
        
        # Word count analysis
        ttk.Button(control_frame, text="Word Count Analysis", 
                  command=lambda: self.run_analysis("word_count")).grid(row=5, column=0, pady=5, sticky=tk.W+tk.E)
        
        # Topic modeling
        ttk.Button(control_frame, text="Topic Modeling", 
                  command=lambda: self.run_analysis("topic_modeling")).grid(row=6, column=0, pady=5, sticky=tk.W+tk.E)
        
        # Similarity analysis
        ttk.Button(control_frame, text="Entry Similarity", 
                  command=lambda: self.run_analysis("similarity")).grid(row=7, column=0, pady=5, sticky=tk.W+tk.E)
        
        # Temporal analysis
        ttk.Button(control_frame, text="Temporal Patterns", 
                  command=lambda: self.run_analysis("temporal")).grid(row=8, column=0, pady=5, sticky=tk.W+tk.E)
        
        # Full analysis
        ttk.Button(control_frame, text="Full Analysis", 
                  command=lambda: self.run_analysis("full")).grid(row=9, column=0, pady=5, sticky=tk.W+tk.E)
        
        # Export options
        ttk.Label(control_frame, text="Export Options:", font=("Arial", 12, "bold")).grid(row=10, column=0, pady=(20, 10), sticky=tk.W)
        
        ttk.Button(control_frame, text="Export Results", 
                  command=self.export_results).grid(row=11, column=0, pady=5, sticky=tk.W+tk.E)
        
        # Status section
        ttk.Label(control_frame, text="Status:", font=("Arial", 12, "bold")).grid(row=12, column=0, pady=(20, 10), sticky=tk.W)
        
        self.status_label = ttk.Label(control_frame, text="Ready", foreground="green")
        self.status_label.grid(row=13, column=0, sticky=tk.W)
        
        # Results display (right side)
        results_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding="10")
        results_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # Results title
        self.results_title = ttk.Label(results_frame, text="Select an analysis option to begin", 
                                      font=("Arial", 12))
        self.results_title.grid(row=0, column=0, pady=(0, 10))
        
        # Results text area
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, height=20, width=60)
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Visualization area (bottom)
        viz_frame = ttk.LabelFrame(main_frame, text="Visualizations", padding="10")
        viz_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        viz_frame.columnconfigure(0, weight=1)
        viz_frame.rowconfigure(0, weight=1)
        
        self.viz_canvas = None
        self.viz_label = ttk.Label(viz_frame, text="Visualizations will appear here after analysis")
        self.viz_label.grid(row=0, column=0)
    
    def auto_load_data(self):
        """Automatically load data if available."""
        if os.path.exists("extracted_entries/am"):
            self.load_amandamap_data()
        if os.path.exists("Chats"):
            self.load_chat_data()
    
    def load_amandamap_data(self):
        """Load AmandaMap data from individual entry files."""
        try:
            am_dir = "extracted_entries/am"
            if not os.path.exists(am_dir):
                messagebox.showerror("Error", f"Directory {am_dir} not found")
                return
            
            self.entries = []
            for filename in os.listdir(am_dir):
                if filename.endswith('.md'):
                    filepath = os.path.join(am_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Parse filename to extract info
                        info = self._parse_filename_info(filename)
                        info['content'] = content
                        info['clean_content'] = content
                        info['word_count'] = len(content.split())
                        
                        self.entries.append(info)
                    except Exception as e:
                        print(f"Error reading {filepath}: {e}")
            
            self.update_status(f"Loaded {len(self.entries)} AmandaMap entries")
            messagebox.showinfo("Success", f"Loaded {len(self.entries)} AmandaMap entries")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load AmandaMap data: {e}")
    
    def load_chat_data(self):
        """Load chat text data if available."""
        try:
            chat_dir = "Chats"
            if not os.path.exists(chat_dir):
                messagebox.showerror("Error", f"Directory {chat_dir} not found")
                return
            
            self.chat_texts = []
            for filename in os.listdir(chat_dir):
                if filename.endswith('.md'):
                    filepath = os.path.join(chat_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        self.chat_texts.append({
                            'filename': filename,
                            'content': content
                        })
                    except Exception as e:
                        print(f"Error reading {filepath}: {e}")
            
            self.update_status(f"Loaded {len(self.chat_texts)} chat files")
            messagebox.showinfo("Success", f"Loaded {len(self.chat_texts)} chat files")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load chat data: {e}")
    
    def _parse_filename_info(self, filename):
        """Parse filename to extract number, date, and entry type."""
        name = filename.replace('.md', '')
        parts = name.split('-', 2)
        
        number = None
        date = None
        entry_type = None
        
        if len(parts) >= 2:
            if parts[0].isdigit():
                number = int(parts[0])
                if len(parts) >= 3 and parts[1] != 'nodate':
                    try:
                        date = datetime.strptime(parts[1], '%Y-%m-%d')
                    except ValueError:
                        pass
            elif parts[0] == 'x':
                if len(parts) >= 3 and parts[1] != 'nodate':
                    try:
                        date = datetime.strptime(parts[1], '%Y-%m-%d')
                    except ValueError:
                        pass
        
        # Determine entry type from filename
        if 'threshold' in name.lower():
            entry_type = 'Threshold'
        elif 'whispered flame' in name.lower():
            entry_type = 'Whispered Flame'
        elif 'field pulse' in name.lower():
            entry_type = 'Field Pulse'
        elif 'flame vow' in name.lower():
            entry_type = 'Flame Vow'
        elif 'anchor site' in name.lower():
            entry_type = 'Anchor Site'
        elif 'protocol' in name.lower():
            entry_type = 'Protocol'
        elif 'entry' in name.lower():
            entry_type = 'Entry'
        else:
            entry_type = 'Other'
        
        return {
            'number': number,
            'date': date,
            'type': entry_type,
            'filename': filename,
            'name': name,
            'has_date': date is not None
        }
    
    def run_analysis(self, analysis_type):
        """Run the selected analysis type."""
        if not self.entries:
            messagebox.showerror("Error", "Please load AmandaMap data first")
            return
        
        print(f"Running {analysis_type} analysis with {len(self.entries)} entries")
        self.update_status(f"Running {analysis_type} analysis...")
        self.results_title.config(text=f"Results: {analysis_type.replace('_', ' ').title()}")
        
        try:
            if analysis_type == "type_distribution":
                self.analyze_entry_types()
            elif analysis_type == "word_count":
                self.analyze_word_counts()
            elif analysis_type == "topic_modeling":
                self.perform_topic_modeling()
            elif analysis_type == "similarity":
                self.analyze_similarity()
            elif analysis_type == "temporal":
                self.analyze_temporal_patterns()
            elif analysis_type == "full":
                self.run_full_analysis()
            
            self.update_status(f"Completed {analysis_type} analysis")
            print(f"Successfully completed {analysis_type} analysis")
            
        except Exception as e:
            error_msg = f"Analysis failed: {e}"
            print(f"ERROR: {error_msg}")
            print(f"Traceback: {e.__traceback__}")
            messagebox.showerror("Error", error_msg)
            self.update_status("Analysis failed")
    
    def analyze_entry_types(self):
        """Analyze entry type distribution."""
        type_counts = defaultdict(int)
        for entry in self.entries:
            type_counts[entry['type']] += 1
        
        # Display results
        result_text = "Entry Type Distribution:\n\n"
        for entry_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            result_text += f"{entry_type}: {count} entries\n"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, result_text)
        
        # Create visualization
        self.create_type_distribution_chart(type_counts)
    
    def analyze_word_counts(self):
        """Analyze word count distribution."""
        word_counts = [entry['word_count'] for entry in self.entries if entry['word_count'] > 0]
        
        if not word_counts:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, "No valid word counts found")
            return
        
        result_text = "Word Count Statistics:\n\n"
        result_text += f"Total entries: {len(self.entries)}\n"
        result_text += f"Entries with content: {len(word_counts)}\n"
        result_text += f"Average words: {np.mean(word_counts):.1f}\n"
        result_text += f"Median words: {np.median(word_counts):.1f}\n"
        result_text += f"Min words: {min(word_counts)}\n"
        result_text += f"Max words: {max(word_counts)}\n"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, result_text)
        
        # Create visualization
        self.create_word_count_chart(word_counts)
    
    def perform_topic_modeling(self):
        """Perform topic modeling on entries."""
        # Preprocess text
        texts = []
        for entry in self.entries:
            content = re.sub(r'\*\*([^*]+)\*\*', r'\1', entry['content'])
            content = re.sub(r'__([^_]+)__', r'\1', content)
            content = re.sub(r'#+ ', '', content)
            content = re.sub(r'---', '', content)
            content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
            content = re.sub(r'\n+', ' ', content)
            content = re.sub(r'\s+', ' ', content).strip()
            texts.append(content)
        
        # Create TF-IDF features
        tfidf = TfidfVectorizer(max_features=500, stop_words='english', min_df=2)
        tfidf_matrix = tfidf.fit_transform(texts)
        
        # Perform LDA
        lda = LatentDirichletAllocation(n_components=5, random_state=42, max_iter=50)
        lda.fit(tfidf_matrix)
        
        # Get feature names
        feature_names = tfidf.get_feature_names_out()
        
        # Display results
        result_text = "Topic Modeling Results (5 topics):\n\n"
        for topic_idx, topic in enumerate(lda.components_):
            top_words = [feature_names[i] for i in topic.argsort()[-10:]]
            result_text += f"Topic {topic_idx + 1}: {', '.join(top_words)}\n\n"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, result_text)
        
        # Create visualization
        self.create_topic_chart(lda, feature_names)
    
    def analyze_similarity(self):
        """Analyze similarity between entries."""
        if len(self.entries) < 2:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, "Need at least 2 entries for similarity analysis")
            return
        
        # Preprocess text
        texts = []
        for entry in self.entries:
            content = re.sub(r'\*\*([^*]+)\*\*', r'\1', entry['content'])
            content = re.sub(r'__([^_]+)__', r'\1', content)
            content = re.sub(r'#+ ', '', content)
            content = re.sub(r'---', '', content)
            content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
            content = re.sub(r'\n+', ' ', content)
            content = re.sub(r'\s+', ' ', content).strip()
            texts.append(content)
        
        # Create TF-IDF features
        tfidf = TfidfVectorizer(max_features=1000, stop_words='english', min_df=2)
        tfidf_matrix = tfidf.fit_transform(texts)
        
        # Calculate similarity
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Find most similar pairs
        n_entries = len(self.entries)
        similarities = []
        
        for i in range(n_entries):
            for j in range(i + 1, n_entries):
                if i < similarity_matrix.shape[0] and j < similarity_matrix.shape[1]:
                    sim = similarity_matrix[i][j]
                    similarities.append({
                        'entry1': f"{self.entries[i]['type']} ({self.entries[i]['filename']})",
                        'entry2': f"{self.entries[j]['type']} ({self.entries[j]['filename']})",
                        'similarity': sim
                    })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Display results
        result_text = "Most Similar Entry Pairs:\n\n"
        for i, sim in enumerate(similarities[:15]):
            result_text += f"{i+1}. {sim['entry1']} ↔ {sim['entry2']}\n"
            result_text += f"   Similarity: {sim['similarity']:.3f}\n\n"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, result_text)
        
        # Create visualization
        self.create_similarity_chart(similarity_matrix)
    
    def analyze_temporal_patterns(self):
        """Analyze temporal patterns in entries."""
        dated_entries = [e for e in self.entries if e['has_date'] and e['date']]
        
        if not dated_entries:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, "No dated entries found for temporal analysis")
            return
        
        # Group by month
        date_counts = defaultdict(int)
        for entry in dated_entries:
            month_key = entry['date'].strftime('%Y-%m')
            date_counts[month_key] += 1
        
        if not date_counts:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, "No valid dates found for temporal analysis")
            return
        
        # Display results
        result_text = "Temporal Pattern Analysis:\n\n"
        result_text += f"Total dated entries: {len(dated_entries)}\n"
        result_text += f"Date range: {min(date_counts.keys())} to {max(date_counts.keys())}\n\n"
        result_text += "Entries per month:\n"
        
        for month, count in sorted(date_counts.items()):
            result_text += f"{month}: {count} entries\n"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, result_text)
        
        # Create visualization
        self.create_temporal_chart(date_counts)
    
    def run_full_analysis(self):
        """Run all analyses."""
        result_text = "Full Analysis Results:\n\n"
        
        # Entry types
        type_counts = defaultdict(int)
        for entry in self.entries:
            type_counts[entry['type']] += 1
        
        result_text += "Entry Type Distribution:\n"
        for entry_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            result_text += f"  {entry_type}: {count}\n"
        
        # Word counts
        word_counts = [entry['word_count'] for entry in self.entries if entry['word_count'] > 0]
        if word_counts:
            result_text += f"\nWord Count Statistics:\n"
            result_text += f"  Average: {np.mean(word_counts):.1f}\n"
            result_text += f"  Median: {np.median(word_counts):.1f}\n"
            result_text += f"  Min: {min(word_counts)}\n"
            result_text += f"  Max: {max(word_counts)}\n"
        
        # Dates
        dated_entries = [e for e in self.entries if e['has_date']]
        result_text += f"\nDated Entries: {len(dated_entries)}\n"
        result_text += f"Undated Entries: {len(self.entries) - len(dated_entries)}\n"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, result_text)
        
        # Create comprehensive visualization
        self.create_full_analysis_chart(type_counts, word_counts, dated_entries)
    
    def create_type_distribution_chart(self, type_counts):
        """Create entry type distribution chart."""
        self.clear_visualization()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        types, counts = zip(*sorted(type_counts.items(), key=lambda x: x[1], reverse=True))
        
        bars = ax.bar(types, counts, color='skyblue', alpha=0.7)
        ax.set_title('Entry Type Distribution', fontsize=14, fontweight='bold')
        ax.set_xlabel('Entry Type')
        ax.set_ylabel('Number of Entries')
        ax.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{count}', ha='center', va='bottom')
        
        plt.tight_layout()
        self.display_chart(fig)
    
    def create_word_count_chart(self, word_counts):
        """Create word count distribution chart."""
        self.clear_visualization()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(word_counts, bins=20, color='lightgreen', alpha=0.7, edgecolor='black')
        ax.set_title('Word Count Distribution', fontsize=14, fontweight='bold')
        ax.set_xlabel('Word Count')
        ax.set_ylabel('Frequency')
        ax.axvline(np.mean(word_counts), color='red', linestyle='--', 
                   label=f'Mean: {np.mean(word_counts):.1f}')
        ax.axvline(np.median(word_counts), color='orange', linestyle='--', 
                   label=f'Median: {np.median(word_counts):.1f}')
        ax.legend()
        
        plt.tight_layout()
        self.display_chart(fig)
    
    def create_topic_chart(self, lda, feature_names):
        """Create topic modeling visualization."""
        self.clear_visualization()
        
        # Determine how many topics we actually have
        n_topics = min(5, lda.components_.shape[0])
        
        if n_topics <= 3:
            # Use 1 row for 3 or fewer topics
            fig, axes = plt.subplots(1, n_topics, figsize=(5*n_topics, 6))
            if n_topics == 1:
                axes = [axes]
        else:
            # Use 2 rows for 4-5 topics
            fig, axes = plt.subplots(2, 3, figsize=(15, 10))
            axes = axes.flatten()
        
        for topic_idx in range(n_topics):
            if topic_idx < len(axes):
                topic = lda.components_[topic_idx]
                # Get top 8 words, but make sure we don't exceed available features
                n_words = min(8, len(feature_names))
                top_indices = topic.argsort()[-n_words:]
                top_words = [feature_names[i] for i in top_indices]
                top_scores = [topic[i] for i in top_indices]
                
                axes[topic_idx].barh(range(len(top_words)), top_scores, color='lightcoral')
                axes[topic_idx].set_yticks(range(len(top_words)))
                axes[topic_idx].set_yticklabels(top_words)
                axes[topic_idx].set_title(f'Topic {topic_idx + 1}')
                axes[topic_idx].set_xlabel('Weight')
        
        # Hide unused subplots
        for i in range(n_topics, len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        self.display_chart(fig)
    
    def create_similarity_chart(self, similarity_matrix):
        """Create similarity matrix heatmap."""
        self.clear_visualization()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Sample a subset for visualization if too large
        if similarity_matrix.shape[0] > 50:
            sample_size = 50
            sample_matrix = similarity_matrix[:sample_size, :sample_size]
            ax.set_title(f'Similarity Matrix (First {sample_size} entries)', fontsize=14, fontweight='bold')
        else:
            sample_matrix = similarity_matrix
            ax.set_title('Similarity Matrix', fontsize=14, fontweight='bold')
        
        im = ax.imshow(sample_matrix, cmap='viridis', aspect='auto')
        ax.set_xlabel('Entry Index')
        ax.set_ylabel('Entry Index')
        
        plt.colorbar(im, ax=ax, label='Similarity Score')
        plt.tight_layout()
        self.display_chart(fig)
    
    def create_temporal_chart(self, date_counts):
        """Create temporal pattern chart."""
        self.clear_visualization()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        months, month_counts = zip(*sorted(date_counts.items()))
        ax.plot(months, month_counts, marker='o', linewidth=2, markersize=6, color='purple')
        ax.set_title('Entries Over Time', fontsize=14, fontweight='bold')
        ax.set_xlabel('Month')
        ax.set_ylabel('Number of Entries')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
        
        # Add value labels on points
        for i, (month, count) in enumerate(zip(months, month_counts)):
            ax.annotate(str(count), (i, count), textcoords="offset points", 
                       xytext=(0,10), ha='center')
        
        plt.tight_layout()
        self.display_chart(fig)
    
    def create_full_analysis_chart(self, type_counts, word_counts, dated_entries):
        """Create comprehensive analysis chart."""
        self.clear_visualization()
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Entry type distribution
        if type_counts:
            types, counts = zip(*sorted(type_counts.items(), key=lambda x: x[1], reverse=True))
            axes[0, 0].bar(types, counts, color='skyblue', alpha=0.7)
            axes[0, 0].set_title('Entry Type Distribution')
            axes[0, 0].tick_params(axis='x', rotation=45)
        else:
            axes[0, 0].text(0.5, 0.5, 'No entry types found', ha='center', va='center', transform=axes[0, 0].transAxes)
            axes[0, 0].set_title('Entry Type Distribution')
        
        # 2. Word count distribution
        if word_counts:
            axes[0, 1].hist(word_counts, bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
            axes[0, 1].set_title('Word Count Distribution')
            axes[0, 1].set_xlabel('Word Count')
            axes[0, 1].set_ylabel('Frequency')
        else:
            axes[0, 1].text(0.5, 0.5, 'No word count data', ha='center', va='center', transform=axes[0, 1].transAxes)
            axes[0, 1].set_title('Word Count Distribution')
        
        # 3. Entry type vs word count
        if type_counts and word_counts:
            type_word_counts = defaultdict(list)
            for entry in self.entries:
                if entry.get('word_count', 0) > 0:
                    type_word_counts[entry['type']].append(entry['word_count'])
            
            if type_word_counts:
                types_list = list(type_word_counts.keys())
                word_count_lists = [type_word_counts[t] for t in types_list]
                
                axes[1, 0].boxplot(word_count_lists, labels=types_list)
                axes[1, 0].set_title('Word Count by Entry Type')
                axes[1, 0].tick_params(axis='x', rotation=45)
            else:
                axes[1, 0].text(0.5, 0.5, 'No word count data by type', ha='center', va='center', transform=axes[1, 0].transAxes)
                axes[1, 0].set_title('Word Count by Entry Type')
        else:
            axes[1, 0].text(0.5, 0.5, 'No data for type vs word count', ha='center', va='center', transform=axes[1, 0].transAxes)
            axes[1, 0].set_title('Word Count by Entry Type')
        
        # 4. Date distribution
        if dated_entries:
            date_counts = defaultdict(int)
            for entry in dated_entries:
                month_key = entry['date'].strftime('%Y-%m')
                date_counts[month_key] += 1
            
            if date_counts:
                months, month_counts = zip(*sorted(date_counts.items()))
                axes[1, 1].plot(months, month_counts, marker='o')
                axes[1, 1].set_title('Entries Over Time')
                axes[1, 1].tick_params(axis='x', rotation=45)
            else:
                axes[1, 1].text(0.5, 0.5, 'No date data', ha='center', va='center', transform=axes[1, 1].transAxes)
                axes[1, 1].set_title('Entries Over Time')
        else:
            axes[1, 1].text(0.5, 0.5, 'No dated entries', ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Entries Over Time')
        
        plt.tight_layout()
        self.display_chart(fig)
    
    def display_chart(self, fig):
        """Display a matplotlib chart in the GUI."""
        self.viz_canvas = FigureCanvasTkAgg(fig, self.root)
        self.viz_canvas.draw()
        
        # Get the widget and place it in the visualization frame
        chart_widget = self.viz_canvas.get_tk_widget()
        
        # Find the visualization frame and place the chart there
        for child in self.root.winfo_children():
            if isinstance(child, ttk.Frame):
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, ttk.LabelFrame) and grandchild.winfo_name() == '':
                        # This is likely our visualization frame
                        chart_widget.grid(row=0, column=0, in_=grandchild)
                        return
        
        # Fallback: place in the main window
        chart_widget.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def export_results(self):
        """Export analysis results to a file."""
        # Check if there are results to export
        if not self.results_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Warning", "No analysis results to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Results exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def update_status(self, message):
        """Update the status label."""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def clear_visualization(self):
        """Clear the current visualization."""
        if self.viz_canvas:
            try:
                self.viz_canvas.get_tk_widget().destroy()
            except:
                pass
            self.viz_canvas = None
        
        # Show the placeholder label
        try:
            self.viz_label.grid()
        except:
            pass

def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    app = AmandaMapGUIAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
