# Gap Hunter Bot

<div align="center">

![Gap Hunter Bot Logo](https://img.shields.io/badge/Gap%20Hunter%20Bot-Academic%20Research-blue?style=for-the-badge&logo=graduation-cap)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.37+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

**AI-Powered Academic Research Gap Identification & Idea Development**

*Transform your research workflow with intelligent gap analysis, novelty scoring, and automated paper discovery*

[Quick Start](#quick-start) • [Documentation](#documentation) • [Web Interface](#web-interface) • [Examples](#usage-examples) • [Support](#troubleshooting)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage Options](#usage-options)
- [Web Interface](#web-interface)
- [Command Line](#command-line)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Contact](#contact)

---

## Overview

**Gap Hunter Bot** is an AI-powered tool designed for academic researchers to automatically identify research gaps, generate novel research ideas, and analyze academic literature. It searches multiple academic databases, extracts real paper information, and provides structured analysis with novelty scoring and Q1 journal rankings.

### Perfect For:
- **Graduate Students** - Finding thesis topics and research directions
- **Researchers** - Identifying gaps in current literature
- **Academic Institutions** - Systematic literature reviews
- **Innovation Teams** - Discovering research opportunities

---

## Key Features

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Multi-Database Search** | Searches Semantic Scholar, CORE, and Crossref APIs | Comprehensive paper coverage |
| **Real Paper Data** | Extracts actual titles, authors, and publication years | Verifiable academic sources |
| **Novelty Scoring** | Assigns 1-5 novelty scores with "rethink" indicators | Prioritize high-impact research |
| **Q1 Journal Ranking** | Identifies top-quartile journal publications | Target prestigious venues |
| **Modern Web Interface** | Streamlit-based UI with interactive charts | User-friendly for all skill levels |
| **Export Options** | Download results as YAML/JSON formats | Easy data integration |
| **Visualization** | Interactive charts and progress tracking | Better insights and UX |
| **Search History** | Track and revisit previous searches | Efficient workflow management |

---

## Quick Start

> **Get started in under 2 minutes!**

### 1. **Launch the Web Interface** (Recommended)
```bash
python web/launch_web_app.py
```

### 2. **Open Your Browser**
The interface will automatically open at: `http://localhost:8501`

### 3. **Enter Research Topic**
Type any academic topic (e.g., "machine learning for healthcare")

### 4. **Get Results**
View research gaps, novelty scores, and export data!

### 5. **Choose Your LLM Provider**
Select from OpenAI, Anthropic Claude, or Google Gemini in the sidebar based on your API access and preferences.

---

## Prerequisites

### **System Requirements**
- **Python 3.8+** (Python 3.9+ recommended)
- **Internet connection** for API access
- **Web browser** for the interface (Chrome, Firefox, Safari, Edge)

### **Dependencies**
All dependencies are automatically installed, including:
- `streamlit` - Web interface framework
- `plotly` - Interactive visualizations
- `pyyaml` - YAML processing
- `requests` - API communication
- `pandas` - Data manipulation

### **LLM Provider API Keys**
You need at least one LLM provider API key:

| Provider | Models Available | Best For | Cost |
|----------|------------------|----------|------|
| **OpenAI** | GPT-4o, GPT-4o-mini, O1 | General purpose, reliable | Medium-High |
| **Anthropic Claude** | Claude-3.5-Sonnet, Claude-3-Haiku | Complex reasoning, safety | Medium |
| **Google Gemini** | Gemini-Pro, Gemini-Pro-Vision | Multimodal, cost-effective | Low-Medium |

**Recommendation:** Start with **OpenAI GPT-4o-mini** for cost-effectiveness or **Claude-3.5-Sonnet** for best quality.

---

## � Installation

### **Option 1: Automatic Setup** (Recommended)
```bash
# Clone or download the project
cd AI-Scientist-v2

# Run the launcher (installs dependencies automatically)
python launch_web_app.py
```

### **Option 2: Manual Installation**
```bash
# Install dependencies
pip install streamlit plotly pyyaml requests pandas

# Launch the application
python launch_web_app.py
```

### **Option 3: Shell Script** (Mac/Linux)
```bash
# Make executable and run
chmod +x start_web_app.sh
./start_web_app.sh
```

---

## 🎮 Usage Options

Gap Hunter Bot offers **three interfaces** to suit different user preferences:

### 🌐 **Web Interface** (Recommended for Most Users)

<div align="center">

![Web Interface](https://img.shields.io/badge/Interface-Web%20Based-brightgreen?style=for-the-badge&logo=streamlit)

</div>

**Perfect for:** Beginners, visual learners, interactive analysis

```bash
python launch_web_app.py
```

**Features:**
- 🎨 Modern, intuitive web interface
- � Interactive charts and visualizations
- 💾 One-click export (YAML/JSON)
- 📱 Mobile-friendly responsive design
- 🔍 Real-time search progress
- 📚 Built-in search history
- 🎯 Visual novelty scoring

### 💻 **Command Line Interface** (For Technical Users)

<div align="center">

![CLI Interface](https://img.shields.io/badge/Interface-Command%20Line-blue?style=for-the-badge&logo=terminal)

</div>

**Perfect for:** Developers, automation, scripting

```bash
python foolproof_start.py
```

**Features:**
- ⚡ Fast execution
- 📝 YAML output format
- 🔧 Scriptable and automatable
- 💻 Terminal-based workflow

### 🎯 **Direct Access** (For Advanced Users)

<div align="center">

![Direct Access](https://img.shields.io/badge/Interface-Direct%20Access-orange?style=for-the-badge&logo=python)

</div>

**Perfect for:** Researchers, custom workflows, integration

```bash
python clean_gap_hunter.py
```

**Features:**
- 🔬 Direct Gap Hunter Bot access
- 🎛️ Full control over parameters
- 🔍 Detailed search process visibility
- 📊 Raw data access

---

## 🌐 Web Interface

### 🎨 **Interface Overview**

The web interface provides a modern, user-friendly experience for academic research gap identification:

#### 🏠 **Main Dashboard**
- **Search Form**: Clean input with example topics
- **Progress Tracking**: Real-time API search status
- **Results Display**: Formatted research gap cards
- **Interactive Charts**: Novelty score distribution

#### 🔧 **Sidebar Features**
- **API Status**: Live connection indicators
- **Search History**: Quick access to previous searches
- **Export Options**: Download YAML/JSON results
- **Settings**: Customization options

#### 📊 **Result Cards**
Each research gap is displayed with:
- 📄 **Paper Information**: Title, author, year
- 🔍 **Research Gap**: Concise description (≤25 words)
- 🏷️ **Keywords**: 3-5 expansion terms
- 📈 **Novelty Score**: 1-5 rating with color coding
- 🏆 **Q1 Status**: Journal ranking indicator
- 🎯 **Next Steps**: Concrete action recommendations

### 🎨 **Visual Design**

#### 🎨 **Color Coding System**
| Score | Color | Meaning | Action |
|-------|-------|---------|--------|
| 🟢 4-5 | Green | High novelty | **Pursue research** |
| 🟡 3 | Yellow | Medium novelty | **Consider refinement** |
| 🔴 1-2 | Red | Low novelty | **Rethink approach** |

#### 🏆 **Journal Rankings**
- 🏆 **Q1 Journal**: Green badge (top quartile)
- 📄 **Non-Q1**: Red badge (other journals)

---

## 💻 Command Line

### 🚀 **Quick Commands**

```bash
# Main launcher with menu
python foolproof_start.py

# Direct Gap Hunter Bot
python clean_gap_hunter.py

# Web interface launcher
python launch_web_app.py

# Test all components
python test_web_interface.py
```

### 📝 **Command Line Workflow**

1. **Start the application**
   ```bash
   python clean_gap_hunter.py
   ```

2. **Enter research topic**
   ```
   🎯 Enter research topic: machine learning for healthcare
   ```

3. **View results**
   ```yaml
   paper: "Smith 2024 Machine Learning Applications in Healthcare"
   gap: "Limited scalability of ML methods in clinical settings"
   keywords: [machine, learning, healthcare, scalability]
   score: 4
   note: ""
   q1: true
   NEXT_STEPS: "Design experiments targeting clinical scalability."
   ```

---

## 💡 Usage Examples

### 🔬 **Example 1: Computer Vision Research**

**Input Topic:** `computer vision`

**Expected Output:**
```yaml
paper: "Johnson 2023 Deep Learning for Medical Image Analysis"
gap: "Lack of interpretability in computer vision diagnostic models"
keywords: [computer, vision, interpretability, medical, deep]
score: 5
note: ""
q1: true
NEXT_STEPS: "Develop interpretable computer vision frameworks for medical diagnosis."
```

### 🧠 **Example 2: Natural Language Processing**

**Input Topic:** `natural language processing`

**Expected Output:**
```yaml
paper: "Chen 2024 Transformer Models for Clinical Text Processing"
gap: "Limited generalization of NLP across different medical domains"
keywords: [natural, language, processing, clinical, generalization]
score: 4
note: ""
q1: false
NEXT_STEPS: "Implement NLP solution incorporating clinical and generalization techniques."
```

### 🏥 **Example 3: Healthcare AI**

**Input Topic:** `artificial intelligence healthcare`

**Expected Output:**
```yaml
paper: "Williams 2023 AI Ethics in Healthcare Applications"
gap: "Ethical implications of AI healthcare applications understudied"
keywords: [artificial, intelligence, healthcare, ethics, applications]
score: 3
note: ""
q1: true
NEXT_STEPS: "Conduct systematic review of ethics methods in AI contexts."
```

---

## Configuration

### **API Keys Setup**

Gap Hunter Bot supports multiple LLM providers. You can use the pre-configured keys or set up your own:

#### **Quick Setup (Pre-configured)**
```bash
python scripts/setup_api_keys.py
```

#### **Custom Setup (Interactive)**
```bash
python scripts/setup_api_keys.py --interactive
```

#### **Manual Setup**
Create a `.env` file in the project root:
```bash
# Core APIs (Required)
GOOGLE_API_KEY=your_google_api_key
S2_API_KEY=your_semantic_scholar_key
CORE_API_KEY=your_core_api_key
CONTACT_EMAIL=your_email@example.com

# LLM Providers (At least one required)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GEMINI_API_KEY=your_gemini_key  # Can be same as GOOGLE_API_KEY
```

### **LLM Provider Selection**

#### **In Web Interface**
1. Open the sidebar in the web interface
2. Select your preferred provider from the dropdown
3. Choose the specific model
4. Click "Save as Default" to persist your choice

#### **In Configuration File**
Edit `config/bfts_config.yaml`:
```yaml
llm_providers:
  default_provider: "openai"  # or "anthropic", "google"
  providers:
    openai:
      default_model: "gpt-4o"
    anthropic:
      default_model: "claude-3-5-sonnet-20241022"
    google:
      default_model: "gemini-pro"
```

### **Provider Comparison**

| Feature | OpenAI | Anthropic Claude | Google Gemini |
|---------|--------|------------------|---------------|
| **Quality** | Excellent | Excellent | Very Good |
| **Speed** | Fast | Fast | Very Fast |
| **Cost** | Medium-High | Medium | Low-Medium |
| **Context Length** | 128K tokens | 200K tokens | 1M tokens |
| **Best Use Case** | General purpose | Complex reasoning | Cost-sensitive |
| **Reliability** | Very High | Very High | High |

### **Advanced Configuration**

For advanced settings, modify:
- `config/bfts_config.yaml` - Main configuration file
- `src/ai_scientist/llm_providers.py` - Provider settings
- `.env` - Environment variables and API keys

---

## � Troubleshooting

### 🔧 **Common Issues & Solutions**

#### ❌ **"Module not found" Error**
```bash
ModuleNotFoundError: No module named 'streamlit'
```
**Solution:**
```bash
pip install streamlit plotly pyyaml requests pandas
```

#### ❌ **"Port already in use" Error**
```bash
OSError: [Errno 48] Address already in use
```
**Solution:**
```bash
# Kill existing Streamlit processes
pkill -f streamlit

# Or use a different port
streamlit run streamlit_app.py --server.port 8502
```

#### ❌ **"API key not found" Error**
**Solution:** The API keys are pre-configured. If you see this error:
1. Restart the application
2. Check your internet connection
3. Contact support if the issue persists

#### ❌ **"Insufficient data for this topic" Error**
**Solution:**
- Try a more general research topic
- Use broader keywords (e.g., "AI" instead of "specific AI algorithm")
- Check your internet connection

#### ❌ **Web Interface Won't Load**
**Solution:**
1. Check if Python 3.8+ is installed: `python --version`
2. Ensure all dependencies are installed
3. Try running: `python test_web_interface.py`
4. Restart your browser and try again

### 🔍 **Debug Mode**

For detailed error information:
```bash
# Run with verbose output
python clean_gap_hunter.py --debug

# Test all components
python test_web_interface.py

# Check Streamlit installation
streamlit --version
```

### 📞 **Getting Help**

If you encounter issues:
1. 📖 Check this documentation
2. 🧪 Run the test suite: `python test_web_interface.py`
3. 📧 Contact support: `calliaobiz@gmail.com`
4. 🐛 Include error messages and system information

---

## � Contributing

We welcome contributions to improve Gap Hunter Bot! Here's how you can help:

### 🎯 **Ways to Contribute**

- 🐛 **Report Bugs**: Found an issue? Let us know!
- 💡 **Suggest Features**: Have ideas for improvements?
- 📝 **Improve Documentation**: Help make instructions clearer
- 🧪 **Add Tests**: Enhance the test suite
- 🎨 **UI/UX Improvements**: Make the interface better

### 📋 **Contribution Guidelines**

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** with clear commit messages
4. **Test your changes**: `python test_web_interface.py`
5. **Submit a pull request** with a clear description

### � **Development Setup**

```bash
# Clone the repository
git clone <repository-url>
cd AI-Scientist-v2

# Install development dependencies
pip install -r requirements.txt

# Run tests
python test_web_interface.py

# Start development server
python launch_web_app.py
```

### 📝 **Code Style**

- Follow PEP 8 Python style guidelines
- Add docstrings to functions and classes
- Include type hints where appropriate
- Write clear, descriptive commit messages

---

## 📚 Additional Resources

### 📖 **Documentation Files**
- `WEB_INTERFACE_GUIDE.md` - Detailed web interface guide
- `STREAMLIT_ENHANCEMENT_SUMMARY.md` - Technical implementation details
- `STREAMLIT_FIX_SUMMARY.md` - Bug fixes and solutions

### 🎓 **Academic Resources**
- [Semantic Scholar API Documentation](https://api.semanticscholar.org/)
- [CORE API Documentation](https://core.ac.uk/docs/)
- [Crossref API Documentation](https://www.crossref.org/documentation/retrieve-metadata/)

### 🛠️ **Technical Resources**
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)
- [PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)

---

## 📧 Contact

### 👨‍💻 **Project Maintainer**
- **Email**: calliaobiz@gmail.com
- **Focus**: Academic research idea development
- **Response Time**: Usually within 24 hours

### � **Support**
For technical support, please include:
- Your operating system (Windows/Mac/Linux)
- Python version (`python --version`)
- Error messages (if any)
- Steps to reproduce the issue

### 💬 **Feedback**
We'd love to hear about your experience:
- Research topics you've explored
- Features you'd like to see
- Success stories using Gap Hunter Bot

---

## 🎉 Ready to Start Research Gap Hunting?

<div align="center">

### 🚀 **Launch Gap Hunter Bot Now!**

```bash
python launch_web_app.py
```

**🌐 Web Interface:** `http://localhost:8501`

---

**🎓 Transform your research workflow with AI-powered gap identification!**

[![Get Started](https://img.shields.io/badge/Get%20Started-Launch%20Now-brightgreen?style=for-the-badge&logo=rocket)](http://localhost:8501)

</div>

---

<div align="center">

**Made with ❤️ for the academic research community**

📧 calliaobiz@gmail.com • 🎓 Academic Research Focus • 🔍 Gap Hunter Bot

</div>
