# AmandaMap GUI Analyzer

A user-friendly graphical interface for analyzing your AmandaMap and Phoenix Codex entries without needing to run TensorFlow from the command line.

## 🚀 Features

### **Interactive Analysis Options**
- **Entry Type Distribution** - See how many of each type (Threshold, Whispered Flame, Field Pulse, etc.)
- **Word Count Analysis** - Statistical analysis of entry lengths
- **Topic Modeling** - Discover hidden themes in your entries using LDA
- **Entry Similarity** - Find which entries are most similar to each other
- **Temporal Patterns** - Analyze how your entries change over time
- **Full Analysis** - Run all analyses at once for comprehensive insights

### **Visualizations**
- Interactive charts and graphs
- Entry type distribution bar charts
- Word count histograms with mean/median lines
- Topic modeling visualizations
- Similarity matrix heatmaps
- Temporal pattern line charts

### **Data Management**
- Auto-loads AmandaMap data from `extracted_entries/am/`
- Loads chat data from `Chats/` directory
- Export results to text files
- Real-time status updates

## 📋 Requirements

- Python 3.7+
- No TensorFlow required! (uses scikit-learn instead)

## 🛠️ Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements_gui.txt
   ```

2. **Run the GUI:**
   ```bash
   python launch_gui.py
   ```
   
   Or directly:
   ```bash
   python amandamap_gui_analyzer.py
   ```

## 🎯 How to Use

### **1. Launch the Application**
- Run `launch_gui.py` or `amandamap_gui_analyzer.py`
- The GUI will automatically load your AmandaMap data if available

### **2. Load Data (if not auto-loaded)**
- Click "Load AmandaMap Data" to load from `extracted_entries/am/`
- Click "Load Chat Data" to load from `Chats/` directory

### **3. Choose Analysis**
- Select from the analysis options on the left panel
- Each analysis will show results in the text area and create visualizations

### **4. View Results**
- **Text Results**: Displayed in the right panel
- **Visualizations**: Appear at the bottom of the window
- **Status**: Shows current operation status

### **5. Export Results**
- Click "Export Results" to save analysis results to a text file

## 🔍 Analysis Types Explained

### **Entry Type Distribution**
Shows how many entries you have of each type:
- Threshold entries
- Whispered Flame entries  
- Field Pulse entries
- Flame Vow entries
- Anchor Site entries
- Protocol entries
- General entries

### **Word Count Analysis**
Statistical breakdown of entry lengths:
- Average, median, min, max word counts
- Distribution histogram
- Comparison across entry types

### **Topic Modeling**
Uses Latent Dirichlet Allocation to find 5 main themes in your content:
- Identifies key words for each topic
- Shows topic weights and relationships
- Helps discover hidden patterns

### **Entry Similarity**
Finds which entries are most similar:
- Uses TF-IDF vectorization
- Cosine similarity scoring
- Shows top 15 most similar pairs

### **Temporal Patterns**
Analyzes how your entries change over time:
- Entries per month
- Date range coverage
- Temporal trends

## 💡 Tips for Best Results

1. **Ensure data is loaded** before running analysis
2. **Use "Full Analysis"** for comprehensive overview
3. **Export results** to save important findings
4. **Check visualizations** for patterns not obvious in text
5. **Compare different analysis types** for deeper insights

## 🐛 Troubleshooting

### **GUI won't launch**
- Check Python version (3.7+ required)
- Install dependencies: `pip install -r requirements_gui.txt`
- Try running directly: `python amandamap_gui_analyzer.py`

### **No data loaded**
- Ensure `extracted_entries/am/` directory exists
- Check file permissions
- Verify markdown files are present

### **Analysis errors**
- Check data is loaded first
- Ensure files contain valid content
- Check console for detailed error messages

## 🔄 Updating

To get the latest version:
1. Pull latest changes from your repository
2. Restart the GUI application
3. New features and improvements will be available

## 📊 Sample Output

The GUI provides rich, interactive analysis including:
- **Text summaries** of all findings
- **Interactive charts** you can zoom and explore
- **Exportable results** for further analysis
- **Real-time status** of operations

This makes it much easier to explore your AmandaMap data than command-line tools!
