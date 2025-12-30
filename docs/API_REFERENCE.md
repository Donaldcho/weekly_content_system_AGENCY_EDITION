# 📚 API Reference & Code Documentation

This document provides a detailed technical breakdown of the classes, functions, and modules in **Deviceterra**. Use this reference when modifying the codebase.

---

## 🏗️ Backend Core (`backend/`)

### 🍌 `NanoBanana` (`backend/nano_banana.py`)
The dedicated image generation engine. It abstracts away the complexity of switching between different Google AI models.

#### Class: `NanoBanana(tier="Pro")`
*   **`__init__(tier)`**: Initializes the Google GenAI client based on the tier configuration.
*   **`generate_image(prompt, output_filename, ...)`**
    *   **The "Universal Switch"**:
        *   Detects if `active_model` is **Gemini** (Multimodal) or **Imagen** (Pure Image).
        *   **Gemini Path**: Calls `client.models.generate_content()` with `response_modalities=['IMAGE']`.
        *   **Imagen Path**: Calls `client.models.generate_images()`.
    *   **Returns**: Absolute path to the saved image file.
*   **`_dream_concept(prompt)`**: Fallback method. Uses Gemini Text to describe a visual concept if the image API fails.

### 🧠 `ContentGenerator` (`backend/content_generator.py`)
The legacy orchestrator (Monolith). Handles state management and high-level workflow.

#### Class: `ContentGenerator`
*   **`generate_weekly_plan(topic, usage_rag)`**:
    *   The entry point for the "Generate Week" button.
    *   **Logic Flow**:
        1.  Calls `MarketingAgency` (ADK) to invoke the **Strategist**.
        2.  Receives a 7-day plan (JSON).
        3.  Iterates through the plan, calling the **Creator Agent** for drafts.
        4.  Returns a list of `Post` objects.
*   **`generate_tailored_image_prompt(post_content, style)`**:
    *   Uses **Prompt Registry** (`smart_style_generator`) to rewrite a blog post into an image prompt.

### 📚 `PromptRegistry` (`backend/prompt_registry.py`)
Decouples system instructions from Python code.

#### Class: `PromptRegistry`
*   **`get(key, **kwargs)`**:
    *   Loads the JSON string from `assets/prompts.json`.
    *   Formats it with dynamic values (e.g., `{topic}`, `{brand_name}`).
    *   **Usage**: `registry.get("visual_agent_system", topic="AI")`.

---

## 🕵️ Agent Development Kit (`backend/adk/`)

### 🏢 `MarketingAgency` (`backend/adk/main.py`)
The Facade pattern controller for the ADK. It manages the lifecycle of specialized agents.

*   **`create_strategy(topic, brand_info)`**: Hires `StrategistAgent` to plan the week.
*   **`generate_visual(...)`**: Hires `VisualDesignAgent` to craft art prompts.
*   **`design_logo(...)`**: Hires `LogoDesignAgent`.

### 🤖 `BaseAdkAgent` (`backend/adk/agents/base.py`)
The parent class for all agents.
*   **`generate(prompt, json_mode=True)`**:
    *   Wrapper around Gemini API.
    *   If `json_mode=True`, forces `response_mime_type="application/json"` to ensure structural stability.

---

## 🖥️ UI Layer (`ui/`)

### `generate.py`
The main interactive page.
*   **`render_generate_page()`**:
    *   Draws the explicit sidebar inputs.
    *   **State Management**: Uses `st.session_state['generated_plan']` to persist data between re-runs.
    *   **Button Logic**:
        *   "Generate Weekly Plan" -> Calls `backend.ContentGenerator`.
        *   "Summon Nano Banana" -> Calls `backend.NanoBanana`.

---

## 💾 Database Schema (`backend/database.py`)

### Table: `posts`
*   `id`: INTEGER PK
*   `topic`: TEZT
*   `platform`: TEXT (LinkedIn/Facebook)
*   `content`: TEXT (The post body)
*   `image_path`: TEXT (Local path to generated image)
*   `status`: TEXT (Draft/Scheduled/Published)
*   `scheduled_date`: DATETIME

### Table: `brand_identity`
*   Stores the JSON blob of the user's configured "Brand DNA".
