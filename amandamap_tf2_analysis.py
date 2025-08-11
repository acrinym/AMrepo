#!/usr/bin/env python3
"""
amandamap_tf2_analysis.py — TensorFlow 2 analysis of AmandaMap data.
Combines structured entries with text analysis for insights and pattern recognition.
"""

import os
import json
import re
import numpy as np
import pandas as pd
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

# TensorFlow imports
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    from tensorflow.keras.preprocessing.text import Tokenizer
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    print(f"TensorFlow version: {tf.__version__}")
except ImportError:
    print("TensorFlow not installed. Install with: pip install tensorflow")
    exit(1)

# Text processing
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_similarity

class AmandaMapAnalyzer:
    def __init__(self, amandamap_file, chat_dir=None):
        """Initialize the AmandaMap analyzer."""
        self.amandamap_file = amandamap_file
        self.chat_dir = chat_dir
        self.entries = []
        self.chat_texts = []
        self.vectorizer = None
        self.model = None
        
    def load_amandamap_data(self):
        """Load AmandaMap data from individual entry files instead of structured markdown."""
        print("Loading AmandaMap data from individual files...")
        
        # Load from the extracted entries directory
        am_dir = "extracted_entries/am"
        if not os.path.exists(am_dir):
            print(f"Directory {am_dir} not found")
            return
        
        for filename in os.listdir(am_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(am_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse filename to extract info
                    info = self._parse_filename_info(filename)
                    info['content'] = content
                    info['clean_content'] = content  # Will be cleaned in preprocessing
                    info['word_count'] = len(content.split())
                    
                    self.entries.append(info)
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
        
        print(f"Loaded {len(self.entries)} entries from individual files")
    
    def _parse_filename_info(self, filename):
        """Parse filename to extract number, date, and entry type."""
        # Remove .md extension
        name = filename.replace('.md', '')
        
        # Extract number and date
        parts = name.split('-', 2)
        
        number = None
        date = None
        entry_type = None
        
        if len(parts) >= 2:
            # Check if first part is a number
            if parts[0].isdigit():
                number = int(parts[0])
                if len(parts) >= 3 and parts[1] != 'nodate':
                    # Try to parse date
                    try:
                        date = datetime.strptime(parts[1], '%Y-%m-%d')
                    except ValueError:
                        pass
            elif parts[0] == 'x':
                number = None
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
    
    def load_chat_data(self):
        """Load chat text data if available."""
        if not self.chat_dir or not os.path.exists(self.chat_dir):
            print("Chat directory not found, skipping chat analysis")
            return
        
        print("Loading chat data...")
        
        for filename in os.listdir(self.chat_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(self.chat_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.chat_texts.append({
                        'filename': filename,
                        'content': content
                    })
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
        
        print(f"Loaded {len(self.chat_texts)} chat files")
    
    def preprocess_text(self):
        """Preprocess text data for analysis."""
        print("Preprocessing text data...")
        
        # Clean entry content
        for i, entry in enumerate(self.entries):
            # Remove markdown formatting
            content = re.sub(r'\*\*([^*]+)\*\*', r'\1', entry['content'])
            content = re.sub(r'__([^_]+)__', r'\1', content)
            content = re.sub(r'#+ ', '', content)
            content = re.sub(r'---', '', content)
            content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
            
            # Clean up whitespace
            content = re.sub(r'\n+', ' ', content)
            content = re.sub(r'\s+', ' ', content).strip()
            
            entry['clean_content'] = content
            entry['word_count'] = len(content.split())
            
            # Debug first few entries
            if i < 3:
                print(f"Entry {i}: type='{entry['type']}', content_length={len(entry['content'])}, clean_length={len(content)}, words={entry['word_count']}")
        
        # Clean chat content
        for chat in self.chat_texts:
            content = re.sub(r'\*\*([^*]+)\*\*', r'\1', chat['content'])
            content = re.sub(r'__([^_]+)__', r'\1', content)
            content = re.sub(r'#+ ', '', content)
            content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
            content = re.sub(r'\n+', ' ', content)
            content = re.sub(r'\s+', ' ', content).strip()
            
            chat['clean_content'] = content
            chat['word_count'] = len(content.split())
        
        print(f"Preprocessing complete. Entry content lengths: {[len(e.get('content', '')) for e in self.entries[:5]]}")
    
    def create_text_embeddings(self):
        """Create TF-IDF embeddings for text analysis."""
        print("Creating text embeddings...")
        
        # Combine all text for vectorization
        all_texts = [entry['clean_content'] for entry in self.entries]
        if self.chat_texts:
            all_texts.extend([chat['clean_content'] for chat in self.chat_texts])
        
        # Create TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2
        )
        
        # Fit and transform
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        
        # Store embeddings
        self.entry_embeddings = tfidf_matrix[:len(self.entries)]
        if self.chat_texts:
            self.chat_embeddings = tfidf_matrix[len(self.entries):]
        
        print(f"Created embeddings with {tfidf_matrix.shape[1]} features")
    
    def analyze_entry_patterns(self):
        """Analyze patterns in AmandaMap entries."""
        print("Analyzing entry patterns...")
        
        # Entry type distribution
        type_counts = defaultdict(int)
        for entry in self.entries:
            type_counts[entry['type']] += 1
        
        print("\nEntry Type Distribution:")
        for entry_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {entry_type}: {count}")
        
        # Word count analysis with safety checks
        word_counts = [entry['word_count'] for entry in self.entries if entry['word_count'] > 0]
        if word_counts:
            print(f"\nWord Count Statistics:")
            print(f"  Average: {np.mean(word_counts):.1f}")
            print(f"  Median: {np.median(word_counts):.1f}")
            print(f"  Min: {min(word_counts)}")
            print(f"  Max: {max(word_counts)}")
        else:
            print("\nWord Count Statistics: No valid entries found")
        
        # Date analysis
        dated_entries = [e for e in self.entries if e['has_date']]
        if dated_entries:
            print(f"\nDated Entries: {len(dated_entries)}")
            print(f"Undated Entries: {len(self.entries) - len(dated_entries)}")
        
        # Debug info
        print(f"\nTotal entries loaded: {len(self.entries)}")
        print(f"Entries with content: {len([e for e in self.entries if e.get('content', '').strip()])}")
        print(f"Entries with word counts: {len([e for e in self.entries if e.get('word_count', 0) > 0])}")
    
    def perform_topic_modeling(self, n_topics=5):
        """Perform LDA topic modeling on entries."""
        print(f"Performing topic modeling with {n_topics} topics...")
        
        # Prepare text data
        texts = [entry['clean_content'] for entry in self.entries]
        
        # Create TF-IDF features
        tfidf = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            min_df=2
        )
        tfidf_matrix = tfidf.fit_transform(texts)
        
        # Perform LDA
        lda = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=50
        )
        lda.fit(tfidf_matrix)
        
        # Get feature names
        feature_names = tfidf.get_feature_names_out()
        
        # Display topics
        print("\nTop Topics in AmandaMap:")
        for topic_idx, topic in enumerate(lda.components_):
            top_words = [feature_names[i] for i in topic.argsort()[-10:]]
            print(f"  Topic {topic_idx + 1}: {', '.join(top_words)}")
    
    def create_similarity_matrix(self):
        """Create similarity matrix between entries."""
        print("Creating similarity matrix...")
        
        if not hasattr(self, 'entry_embeddings'):
            print("No embeddings available. Run create_text_embeddings() first.")
            return
        
        # Calculate cosine similarity
        similarity_matrix = cosine_similarity(self.entry_embeddings)
        
        # Find most similar entry pairs
        n_entries = len(self.entries)
        similarities = []
        
        for i in range(n_entries):
            for j in range(i + 1, n_entries):
                sim = similarity_matrix[i][j]
                similarities.append({
                    'entry1': self.entries[i]['type'],
                    'entry2': self.entries[j]['type'],
                    'similarity': sim
                })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        print("\nMost Similar Entry Pairs:")
        for i, sim in enumerate(similarities[:10]):
            print(f"  {sim['entry1']} ↔ {sim['entry2']}: {sim['similarity']:.3f}")
    
    def build_neural_classifier(self):
        """Build a neural network classifier for entry types."""
        print("Building neural classifier...")
        
        # Prepare data
        texts = [entry['clean_content'] for entry in self.entries]
        labels = [entry['type'] for entry in self.entries]
        
        # Create label encoder
        unique_labels = list(set(labels))
        label_to_idx = {label: idx for idx, label in enumerate(unique_labels)}
        encoded_labels = [label_to_idx[label] for label in labels]
        
        # Tokenize text
        tokenizer = Tokenizer(num_words=1000, oov_token='<OOV>')
        tokenizer.fit_on_texts(texts)
        
        # Convert to sequences
        sequences = tokenizer.texts_to_sequences(texts)
        padded_sequences = pad_sequences(sequences, maxlen=100, padding='post', truncating='post')
        
        # Convert to numpy arrays
        X = np.array(padded_sequences)
        y = tf.keras.utils.to_categorical(encoded_labels, num_classes=len(unique_labels))
        
        # Split data
        split_idx = int(0.8 * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Build model
        self.model = keras.Sequential([
            layers.Embedding(1000, 16, input_length=100),
            layers.GlobalAveragePooling1D(),
            layers.Dense(24, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(len(unique_labels), activation='softmax')
        ])
        
        # Compile model
        self.model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Train model
        print("Training neural classifier...")
        history = self.model.fit(
            X_train, y_train,
            epochs=10,
            validation_data=(X_test, y_test),
            verbose=1
        )
        
        # Evaluate
        test_loss, test_acc = self.model.evaluate(X_test, y_test, verbose=0)
        print(f"Test accuracy: {test_acc:.3f}")
        
        return history
    
    def visualize_patterns(self):
        """Create visualizations of patterns."""
        print("Creating visualizations...")
        
        # Set up plotting
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Entry type distribution
        type_counts = defaultdict(int)
        for entry in self.entries:
            type_counts[entry['type']] += 1
        
        types, counts = zip(*sorted(type_counts.items(), key=lambda x: x[1], reverse=True))
        axes[0, 0].bar(types, counts)
        axes[0, 0].set_title('Entry Type Distribution')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. Word count distribution
        word_counts = [entry['word_count'] for entry in self.entries]
        axes[0, 1].hist(word_counts, bins=20, alpha=0.7)
        axes[0, 1].set_title('Word Count Distribution')
        axes[0, 1].set_xlabel('Word Count')
        axes[0, 1].set_ylabel('Frequency')
        
        # 3. Entry type vs word count
        type_word_counts = defaultdict(list)
        for entry in self.entries:
            type_word_counts[entry['type']].append(entry['word_count'])
        
        types_list = list(type_word_counts.keys())
        word_count_lists = [type_word_counts[t] for t in types_list]
        
        axes[1, 0].boxplot(word_count_lists, labels=types_list)
        axes[1, 0].set_title('Word Count by Entry Type')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 4. Date distribution (if available)
        dated_entries = [e for e in self.entries if e['has_date'] and e['date']]
        if dated_entries:
            try:
                dates = [datetime.strptime(e['date'], '%Y-%m-%d') for e in dated_entries if e['date']]
                if dates:
                    date_counts = defaultdict(int)
                    for date in dates:
                        date_counts[date.strftime('%Y-%m')] += 1
                    
                    months, month_counts = zip(*sorted(date_counts.items()))
                    axes[1, 1].plot(months, month_counts, marker='o')
                    axes[1, 1].set_title('Entries Over Time')
                    axes[1, 1].tick_params(axis='x', rotation=45)
                else:
                    axes[1, 1].text(0.5, 0.5, 'No valid dates found', ha='center', va='center', transform=axes[1, 1].transAxes)
                    axes[1, 1].set_title('Entries Over Time')
            except Exception as e:
                print(f"Error processing dates: {e}")
                axes[1, 1].text(0.5, 0.5, f'Date processing error: {e}', ha='center', va='center', transform=axes[1, 1].transAxes)
                axes[1, 1].set_title('Entries Over Time')
        else:
            axes[1, 1].text(0.5, 0.5, 'No dated entries', ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Entries Over Time')
        
        plt.tight_layout()
        plt.savefig('amandamap_analysis.png', dpi=300, bbox_inches='tight')
        print("Saved visualization to 'amandamap_analysis.png'")
    
    def run_full_analysis(self):
        """Run the complete analysis pipeline."""
        print("=" * 60)
        print("AMANDAMAP TF2 ANALYSIS")
        print("=" * 60)
        
        # Load data
        self.load_amandamap_data()
        self.load_chat_data()
        
        # Preprocess
        self.preprocess_text()
        
        # Create embeddings
        self.create_text_embeddings()
        
        # Run analyses
        self.analyze_entry_patterns()
        self.perform_topic_modeling()
        self.create_similarity_matrix()
        
        # Build neural classifier
        try:
            self.build_neural_classifier()
        except Exception as e:
            print(f"Neural classifier failed: {e}")
        
        # Create visualizations
        self.visualize_patterns()
        
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)

def main():
    """Main function to run the analysis."""
    
    # Initialize analyzer
    analyzer = AmandaMapAnalyzer(
        amandamap_file="AMANDA_MAP_STRUCTURED.md",
        chat_dir="Chats"
    )
    
    # Run full analysis
    analyzer.run_full_analysis()

if __name__ == "__main__":
    main()
