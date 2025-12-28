import os
import shutil
import time
from datetime import datetime
from typing import List, Dict, Optional

class VaultManager:
    def __init__(self, vault_dir: str):
        self.vault_dir = vault_dir
        self.ensure_vault_exists()

    def ensure_vault_exists(self):
        """Ensure the vault directory exists."""
        if not os.path.exists(self.vault_dir):
            os.makedirs(self.vault_dir)

    def get_assets(self, filter_type: Optional[str] = None) -> List[Dict]:
        """
        Get list of assets in the vault.
        
        Args:
            filter_type: Optional filter (e.g., 'image', 'video')
            
        Returns:
            List of dicts containing asset info
        """
        assets = []
        if not os.path.exists(self.vault_dir):
            return assets

        valid_image_exts = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
        valid_video_exts = {'.mp4', '.mov', '.avi', '.webm'}

        for filename in os.listdir(self.vault_dir):
            if filename.startswith('.'):
                continue
                
            filepath = os.path.join(self.vault_dir, filename)
            if not os.path.isfile(filepath):
                continue

            stat = os.stat(filepath)
            ext = os.path.splitext(filename)[1].lower()
            
            asset_type = 'other'
            if ext in valid_image_exts:
                asset_type = 'image'
            elif ext in valid_video_exts:
                asset_type = 'video'

            if filter_type and filter_type != 'all' and asset_type != filter_type:
                continue

            assets.append({
                'filename': filename,
                'path': filepath,
                'type': asset_type,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'modified_timestamp': stat.st_mtime
            })

        # Sort by newest first
        return sorted(assets, key=lambda x: x['modified_timestamp'], reverse=True)

    def save_asset(self, file_obj, filename: str) -> Optional[str]:
        """
        Save an uploaded file to the vault.
        
        Args:
            file_obj: The file object (bytes) or UploadedFile from streamlit
            filename: The target filename
            
        Returns:
            Path to saved file or None if failed
        """
        try:
            target_path = os.path.join(self.vault_dir, filename)
            
            # handle duplicates by appending timestamp
            if os.path.exists(target_path):
                base, ext = os.path.splitext(filename)
                timestamp = int(time.time())
                target_path = os.path.join(self.vault_dir, f"{base}_{timestamp}{ext}")

            with open(target_path, "wb") as f:
                f.write(file_obj.read())
            
            return target_path
        except Exception as e:
            print(f"Error saving asset: {e}")
            return None

    def delete_asset(self, filename: str) -> bool:
        """Delete an asset from the vault."""
        try:
            filepath = os.path.join(self.vault_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            print(f"Error deleting asset: {e}")
            return False

    def get_asset_path(self, filename: str) -> str:
        """Get full path for an asset."""
        return os.path.join(self.vault_dir, filename)

    # --- Style Gallery Management ---
    def get_styles(self):
        """Returns list of style reference images."""
        styles_dir = os.path.join(os.path.dirname(self.vault_dir), "styles")
        if not os.path.exists(styles_dir):
            os.makedirs(styles_dir)
            
        styles = []
        for filename in os.listdir(styles_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                styles.append(filename)
        return styles

    def save_style(self, file_obj, filename):
        """Saves a style reference image."""
        styles_dir = os.path.join(os.path.dirname(self.vault_dir), "styles")
        if not os.path.exists(styles_dir):
            os.makedirs(styles_dir)
            
        try:
            target_path = os.path.join(styles_dir, filename)
            # Simple overwrite protection
            if os.path.exists(target_path):
                base, ext = os.path.splitext(filename)
                timestamp = int(time.time())
                target_path = os.path.join(styles_dir, f"{base}_{timestamp}{ext}")
                
            with open(target_path, "wb") as f:
                f.write(file_obj.read())
            return target_path
        except Exception as e:
            print(f"Error saving style: {e}")
            return None
            
    def get_style_path(self, filename):
         return os.path.join(os.path.dirname(self.vault_dir), "styles", filename)
