import os
from supabase import create_client
from config import IS_PRODUCTION, UPLOAD_FOLDER
from supabase_config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET

class StorageHandler:
    def __init__(self):
        if IS_PRODUCTION:
            self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
    def store_file(self, content, filename):
        """Store file in either local storage or Supabase Storage"""
        if IS_PRODUCTION:
            return self._store_supabase(content, filename)
        else:
            return self._store_local(content, filename)
    
    def get_file_url(self, filename):
        """Get URL for accessing the file"""
        if IS_PRODUCTION:
            try:
                # Get a signed URL that expires in 1 hour (3600 seconds)
                response = self.supabase.storage.from_(SUPABASE_BUCKET).create_signed_url(
                    path=f'resumes/{filename}',
                    expires_in=3600
                )
                return response['signedURL']
            except Exception as e:
                print(f"Error generating signed URL: {e}")
                return None
        else:
            # In development, serve through Flask server
            return f'http://localhost:5500/tmp/{filename}'
    
    def delete_file(self, filename):
        """Delete file from storage"""
        if IS_PRODUCTION:
            try:
                self.supabase.storage.from_(SUPABASE_BUCKET).remove([f'resumes/{filename}'])
            except Exception as e:
                print(f"Error deleting file: {e}")
        else:
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
    
    def _store_supabase(self, content, filename):
        """Store file in Supabase Storage"""
        try:
            # Convert content to bytes if it's a string
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            # Upload file to Supabase bucket
            self.supabase.storage.from_(SUPABASE_BUCKET).upload(
                path=f'resumes/{filename}',
                file=content,
                file_options={"content-type": "text/markdown"}
            )
            return filename
        except Exception as e:
            print(f"Error uploading to Supabase: {e}")
            return None
    
    def _store_local(self, content, filename):
        """Store file locally"""
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return filename
        except Exception as e:
            print(f"Error writing to file: {e}")
            if os.path.exists(filepath):
                os.remove(filepath)
            return None 