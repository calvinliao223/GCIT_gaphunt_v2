# 🌐 Gap Hunter Bot - Web Interface Guide

## 🎉 **NEW: Modern Streamlit Web Interface!**

We've enhanced the Gap Hunter Bot with a beautiful, user-friendly web interface that makes academic research gap identification easier than ever!

## 🚀 **Quick Start**

### Option 1: **One-Click Launch** (Recommended)
```bash
python launch_web_app.py
```

### Option 2: **Shell Script** (Mac/Linux)
```bash
./start_web_app.sh
```

### Option 3: **Direct Streamlit**
```bash
streamlit run streamlit_app.py
```

## 🎨 **Web Interface Features**

### 🔍 **Smart Search Interface**
- **Clean input form** for entering research topics
- **Real-time progress indicators** showing API search status
- **Example topics** to help users get started
- **Search history** for quick access to previous searches

### 📊 **Rich Data Visualization**
- **Interactive charts** showing novelty score distribution
- **Color-coded results** based on research gap quality
- **Q1 journal indicators** with visual badges
- **Formatted paper information** display

### 💾 **Export & Download Options**
- **YAML export** (original format as specified)
- **JSON export** for data analysis
- **Timestamped filenames** for organization
- **One-click download** buttons in sidebar

### 📱 **User Experience**
- **Responsive design** works on desktop and mobile
- **Progress tracking** during API searches
- **Error handling** with helpful messages
- **Search suggestions** and examples

## 🎯 **How to Use the Web Interface**

### 1. **Start the Application**
```bash
python launch_web_app.py
```
- The web browser will open automatically
- If not, go to: http://localhost:8501

### 2. **Enter Research Topic**
- Type your research topic in the search box
- Examples: "machine learning", "computer vision", "natural language processing"
- Click "🔍 Hunt Gaps" to start the search

### 3. **View Results**
- **Summary metrics** at the top (papers found, avg score, Q1 journals)
- **Individual research gaps** with expandable details
- **YAML output** for each result
- **Novelty score chart** showing distribution

### 4. **Export Results**
- Use sidebar **"Export Results"** section
- Download as **YAML** or **JSON** format
- Files include timestamp for organization

## 📋 **Web Interface Components**

### 🏠 **Main Dashboard**
- **Header** with Gap Hunter Bot branding
- **Search form** with topic input and examples
- **Results display** with formatted cards
- **Charts and visualizations**

### 🔧 **Sidebar Features**
- **API Status** indicators (Semantic Scholar, CORE, Crossref)
- **Recent Searches** for quick access
- **Export Options** (YAML/JSON downloads)
- **Search History** management

### 📄 **Result Cards**
Each research gap is displayed in an expandable card with:
- **Paper information** (title, author, year)
- **Research gap** description
- **Keywords** as badges
- **Novelty score** with color coding
- **Q1 journal status** indicator
- **Next steps** recommendations
- **YAML output** section

## 🎨 **Visual Design**

### 🎨 **Color Coding**
- **🟢 Green (Score 4-5)**: High novelty, good research opportunity
- **🟡 Yellow (Score 3)**: Medium novelty, consider refinement
- **🔴 Red (Score 1-2)**: Low novelty, "rethink" needed

### 🏆 **Journal Rankings**
- **🏆 Q1 Journal**: Green badge for top-quartile journals
- **📄 Non-Q1**: Red badge for other journals

### 📊 **Charts**
- **Bar chart** showing novelty score distribution
- **Interactive** with hover details
- **Color gradient** from red (low) to green (high)

## 🔧 **Technical Details**

### 📦 **Dependencies**
- **Streamlit**: Web framework
- **Plotly**: Interactive charts
- **PyYAML**: YAML processing
- **Pandas**: Data handling

### 🔑 **API Integration**
- **Semantic Scholar API**: Academic paper search
- **CORE API**: Open access research
- **Crossref API**: Citation database
- **Pre-configured API keys** included

### 💾 **Data Flow**
1. User enters research topic
2. Backend searches multiple APIs
3. Papers filtered and processed
4. Research gaps identified
5. Results formatted and displayed
6. Export options available

## 🆚 **Web vs Command Line**

| Feature | Web Interface | Command Line |
|---------|---------------|--------------|
| **Ease of Use** | ✅ Very Easy | ⚠️ Technical |
| **Visualizations** | ✅ Charts & Graphs | ❌ Text Only |
| **Export Options** | ✅ YAML/JSON | ⚠️ YAML Only |
| **Search History** | ✅ Built-in | ❌ Manual |
| **Progress Tracking** | ✅ Real-time | ⚠️ Basic |
| **Mobile Friendly** | ✅ Responsive | ❌ Desktop Only |

## 🎯 **Best Practices**

### 📝 **Research Topics**
- Use **specific terms** for better results
- Try **multiple variations** of your topic
- Include **domain keywords** (e.g., "machine learning for healthcare")

### 🔍 **Interpreting Results**
- Focus on **high novelty scores** (4-5) for new research
- Consider **Q1 journals** for publication targets
- Use **keywords** for literature review expansion
- Follow **next steps** for research planning

### 💾 **Data Management**
- **Export results** for future reference
- **Save YAML files** for research documentation
- **Track search history** for systematic reviews

## 🚀 **Getting Started**

1. **Launch the web app**: `python launch_web_app.py`
2. **Enter a research topic**: e.g., "artificial intelligence"
3. **Review the results**: Check novelty scores and Q1 status
4. **Export your data**: Download YAML/JSON for analysis
5. **Explore more topics**: Use search history for efficiency

## 📧 **Support**

- **Contact**: calliaobiz@gmail.com
- **Documentation**: This guide and START_HERE.md
- **Issues**: Check console output for error messages

**The web interface makes Gap Hunter Bot accessible to all researchers, from beginners to experts!** 🎓
