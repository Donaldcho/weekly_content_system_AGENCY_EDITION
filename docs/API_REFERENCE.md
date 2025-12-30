# 📚 API Reference & Code Documentation

This document provides a detailed technical breakdown of the classes, functions, and modules in **Deviceterra**. Use this reference when modifying the codebase.

---

## 🏗️ Core Engines (`backend/`)

### 🍌 `NanoBanana` (`backend/nano_banana.py`)
The dedicated image generation engine.
*   **`generate_image(prompt, ...)`**: The Universal Switch (Gemini/Imagen).
*   **`_dream_concept(prompt)`**: Fallback method using text-to-image description.

### 🧠 `ContentGenerator` (`backend/content_generator.py`)
The central orchestrator for weekly planning.
*   **`generate_weekly_plan(topic)`**: Coordinates Strategist/Creator agents.
*   **`generate_campaign(topic, source_text)`**: Used by the **Multiplier** to repurposed content.

### 📡 `SentinelAgent` (`backend/sentinel_agent.py`)
Handles social listening and scraping.
*   **`monitor_competitors()`**: Scrapes configured URLs/APIs for competitor updates. Returns a list of `Alert` objects.
*   **`fetch_trends()`**: analyzing global trends and returns `Trend` objects with `growth` and `relevance` scores.
*   **`analyze_brand_mentions()`**: Performs sentiment analysis on retrieved text corpus.

### 🎬 `VideoDirector` (`backend/video_director.py`)
Manages the script-to-video pipeline.
*   **`generate_script(topic)`**: Uses LLM to write a 3-act script.
*   **`create_storyboard(script)`**: Breaks script into scenes and generates image prompts for each.
*   **`render_video(storyboard_assets)`**: (Experimental) stitches images + audio using ffmpeg wrapper.

### 🎨 `CanvasEngine` (`backend/canvas_engine.py`)
Backend logic for the Visual Editor.
*   **`apply_filter(image_path, filter_name)`**: Applies PIL image enhancements.
*   **`composite_layer(base_image, overlay_image, position)`**: Merges layers.

### 💬 `CommunityAgent` (`backend/community_agent.py`)
Manages the Combined Inbox.
*   **`fetch_messages(folder)`**: Retrieves messages from DB mock or API.
*   **`generate_smart_reply(message_context)`**: Uses Gemini to draft 3 response options.

---

## 🕵️ Agent Development Kit (`backend/adk/`)
The modular brain of the system.

### `MarketingAgency` (`backend/adk/main.py`)
*   **`create_strategy(topic)`**: Hires `StrategistAgent`.
*   **`generate_visual(...)`**: Hires `VisualDesignAgent`.
*   **`build_website(...)`**: Hires `WebDevAgent`.

### `BaseAdkAgent` (`backend/adk/agents/base.py`)
*   **`generate(prompt, json_mode)`**: Wrapper for consistent JSON outputs from Gemini.

---

## 💾 Database Schema (`backend/database.py`)
*   **`posts`**: Weekly content.
*   **`brand_identity`**: Brand DNA.
*   **`messages`**: Inbox data for Community Central.
*   **`competitor_intel`**: Stored alerts from Sentinel.

---

## 📚 `PromptRegistry` (`backend/prompt_registry.py`)
The configuration engine for Agent Personalities.
*   **`assets/prompts.json`**: Edit this file to change the behavior of any agent without touching code.
