# Vision

Vision is a modular Python-based Vision Language Model (VLM) toolkit and application. It provides a comprehensive suite of vision-based "skills" to analyze, describe, and extract information from images, alongside an evaluation harness and a Streamlit-based user interface.

## 🌟 Features

- **Modular Vision Skills**: A variety of specialized capabilities:
  - `analyze_chart`: Interpret and describe charts and graphs.
  - `compare_images`: Identify differences or similarities between multiple images.
  - `describe_scene`: Generate detailed textual descriptions of visual scenes.
  - `detect_objects`: Identify and locate specific objects within an image.
  - `extract_structured`: Pull structured data (like JSON) from visual documents.
  - `read_text`: Perform Optical Character Recognition (OCR).
  - `verify_claim`: Cross-check visual evidence against text claims.
- **Evaluation Harness**: Built-in tools (`app/evals` and `harness/`) to evaluate VLM outputs using LLM judges, semantic similarity, and consistency checks.
- **Streamlit UI**: An interactive web frontend (`ui/streamlit_app.py`) for end-users to easily interact with the vision skills.
- **Observability Integrated**: Direct integration with Langfuse (`app/langfuse_client.py`) for tracking LLM/VLM traces and metrics.

## 📂 Project Structure

```text
Vision/
├── app/                  # Main application logic and backend
│   ├── evals/            # Evaluation metrics (LLM judge, semantic similarity)
│   ├── skills/           # Individual VLM capabilities
│   ├── config.py         # Application configurations
│   ├── langfuse_client.py# Langfuse integration for observability
│   ├── vlm_client.py     # Wrapper for Vision Language Model API calls
│   └── main.py           # Core backend entry point
├── harness/              # Testing and evaluation harness
│   ├── runner.py         # Test execution
│   └── report.py         # Evaluation reports and thresholds
├── scripts/              # Utility scripts (e.g., seeding data, generating docs)
├── ui/                   # Frontend applications
│   └── streamlit_app.py  # Streamlit UI dashboard
├── requirements.txt      # Python dependencies
└── myenv/                # Virtual environment
```

## 🚀 Setup & Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
   cd Vision
   ```

2. **Create and activate a virtual environment:**

   ```bash
   # Windows
   python -m venv myenv
   .\myenv\Scripts\activate

   # macOS/Linux
   python3 -m venv myenv
   source myenv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add your required API keys (e.g., OpenAI, Groq, Langfuse, etc.).

## 💻 Usage

### Running the Streamlit UI

To start the interactive frontend dashboard:

```bash
streamlit run ui/streamlit_app.py
```

### Running Evaluations

To run the evaluation harness over your dataset:

```bash
python -m harness.runner
```

## 🛠 Skills & Extensibility

All vision features are registered in `app/skill_registry.py`. To add a new skill, create a new python file in the `app/skills/` directory extending the base skill class, and register it in the registry.
