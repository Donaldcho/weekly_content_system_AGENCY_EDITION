import uuid
import streamlit as st # Optional, for caching if needed, but keeping it clean
from backend.database import Database
from backend.vault import VaultManager

class TemplateManager:
    def __init__(self, db: Database, vault: VaultManager):
        self.db = db
        self.vault = vault

    def get_templates(self):
        """Returns the list of saved visual templates."""
        settings = self.db.get_brand_settings()
        # Handle simple string case just in case
        if isinstance(settings, str): 
             return [] 
        return settings.get("templates", [])

    def add_template(self, name, description, image_file=None):
        """
        Adds a new visual template.
        Args:
            name: Display name
            description: The prompt/style description
            image_file: Streamlit UploadedFile (optional)
        """
        settings = self.db.get_brand_settings()
        if isinstance(settings, str): settings = {}
        
        templates = settings.get("templates", [])
        
        image_filename = None
        if image_file:
            # Use vault to save style image
            # Create a unique name
            ext = image_file.name.split('.')[-1]
            unique_name = f"tpl_{uuid.uuid4().hex[:8]}.{ext}"
            saved_path = self.vault.save_style(image_file, unique_name)
            if saved_path:
                image_filename = unique_name

        new_template = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "image": image_filename
        }
        
        templates.append(new_template)
        settings["templates"] = templates
        self.db.save_brand_settings(settings)
        return new_template

    def delete_template(self, template_id):
        """Deletes a template by ID."""
        settings = self.db.get_brand_settings()
        if isinstance(settings, str): return False
        
        templates = settings.get("templates", [])
        original_count = len(templates)
        
        # Filter out
        new_templates = [t for t in templates if t["id"] != template_id]
        
        if len(new_templates) < original_count:
            settings["templates"] = new_templates
            self.db.save_brand_settings(settings)
            return True
        return False
