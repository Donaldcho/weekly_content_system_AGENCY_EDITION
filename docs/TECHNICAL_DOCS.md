# Deviceterra Enterprise: Technical Documentation 🛠️

## 🏗️ System Architecture

Deviceterra is a **Single-Page Application (SPA)** built with Python and Streamlit, utilizing a modular **Backend-for-Frontend (BFF)** pattern.

### Core Components
1.  **UI Layer (`ui/`)**: Streamlit components handling rendering and state management (`st.session_state`).
2.  **Orchestrator (`backend/content_generator.py`)**: The central brain that manages the `ContentGenerator` class. It initializes agents and manages the data flow between them.
3.  **Agent Layer (`backend/agents/`)**: Specialized classes inheriting from `BaseAgent`.
4.  **Data Layer (`backend/database.py`)**: A local SQLite wrapper handling all persistence.
5.  **Intelligence Layer**: Google Gemini API (wrapping `google.generativeai`).

---

## 🧠 The Agent Protocol

All agents inherit from `BaseAgent` (`backend/agents/base_agent.py`), which provides:
- **Automatic Configuration**: Loads API keys from `.env`.
- **Cost Intelligence**: Automatically intercepts `response.usage_metadata` and logs it to the `api_logs` table via `self.db.log_usage()`.
- **Error Handling**: Standardized try/except blocks.

### Specialized Agents
*   **Strategist (`strategist.py`)**: Uses Chain-of-Thought (CoT) to break down topics into daily angles.
*   **Creator (`creator.py`)**: Few-shot prompting specialist for copywriting.
*   **Sentinel (`sentinel_agent.py`)**: Simulates high-frequency social listening data and uses LLM for Batch Sentiment Analysis.
*   **ComplianceGuard (`compliance_guard.py`)**: A "Constitutional AI" implementation that validates output against a JSON set of `banned_words` and `anti_patterns`.

---

## 💾 Database Schema (SQLite)

The system uses a single SQLite file (`memory/weekly_content.db`). Key tables:

### `api_logs` (Cost Tracking)
| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary Key |
| agent_name | TEXT | e.g., "StrategistAgent" |
| model | TEXT | e.g., "gemini-1.5-pro" |
| input_tokens | INT | Prompt usage |
| output_tokens | INT | Completion usage |
| cost_usd | REAL | Calculated cost based on dynamic pricing table |

### `users` (RBAC)
| Column | Type | Description |
|--------|------|-------------|
| username | TEXT | Unique identifier |
| role | TEXT | 'admin', 'editor', 'writer' |

### `posts` (Content)
Stores lifecycle of a post.
- `status`: 'draft', 'scheduled', 'posted'
- `content`: JSON blob containing platform drafts, image prompts, and review scores.

---

## 💰 Pricing Logic
Costs are calculated in `backend/database.py` -> `log_usage()`.
We support **Dynamic Pricing** based on model IDs:
- **Flash/Standard**: ~$0.075 - $0.40 per 1M tokens.
- **Pro/Premium**: ~$1.25 - $5.00 per 1M tokens.
- **Banana (Image)**: Fixed cost override ($0.04/img).

---

## 🔒 Security Model
- **Authentication**: Simple session-based boolean `is_authenticated`.
- **Credential Storage**: API Keys are loaded from environment variables (`Config` class). OAuth tokens are stored encrypted (in theory, currently plain text for demo) in `social_tokens` table.
- **Role Enforcement**: UI components check `st.session_state.current_user['role']` before rendering sensitive actions (e.g., "Approve" button).
