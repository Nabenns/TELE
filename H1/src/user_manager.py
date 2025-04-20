import os
import json
import logging
from typing import List, Dict, Union, Optional

logger = logging.getLogger(__name__)

class UserManager:
    """
    Kelas untuk mengelola akses pengguna ke bot
    """
    def __init__(self, users_file: str = 'config/users.json'):
        """
        Inisialisasi UserManager
        
        Args:
            users_file: Path ke file JSON untuk menyimpan data pengguna
        """
        self.users_file = users_file
        self.admins = []  # List user_id admin
        self.allowed_users = []  # List user_id pengguna yang diizinkan
        
        # Buat direktori jika belum ada
        os.makedirs(os.path.dirname(users_file), exist_ok=True)
        
        # Load user data jika file ada
        self.load_users()
    
    def load_users(self) -> None:
        """Load data pengguna dari file"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    data = json.load(f)
                    self.admins = data.get('admins', [])
                    self.allowed_users = data.get('allowed_users', [])
                logger.info(f"Loaded {len(self.admins)} admins and {len(self.allowed_users)} allowed users")
            else:
                # Jika file belum ada, buat file kosong
                self.save_users()
                logger.info(f"Created new users file at {self.users_file}")
        except Exception as e:
            logger.error(f"Error loading users: {str(e)}")
            # Buat data kosong jika terjadi error
            self.admins = []
            self.allowed_users = []
    
    def save_users(self) -> None:
        """Simpan data pengguna ke file"""
        try:
            data = {
                'admins': self.admins,
                'allowed_users': self.allowed_users
            }
            with open(self.users_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved user data with {len(self.admins)} admins and {len(self.allowed_users)} allowed users")
        except Exception as e:
            logger.error(f"Error saving users: {str(e)}")
    
    def is_admin(self, user_id: int) -> bool:
        """
        Cek apakah user adalah admin
        
        Args:
            user_id: ID pengguna Telegram
        
        Returns:
            bool: True jika user adalah admin
        """
        return user_id in self.admins
    
    def is_allowed(self, user_id: int) -> bool:
        """
        Cek apakah user diizinkan mengakses bot
        
        Args:
            user_id: ID pengguna Telegram
        
        Returns:
            bool: True jika user diizinkan (admin atau dalam daftar allowed_users)
        """
        return user_id in self.admins or user_id in self.allowed_users
    
    def add_admin(self, user_id: int) -> bool:
        """
        Tambahkan admin baru
        
        Args:
            user_id: ID pengguna Telegram
        
        Returns:
            bool: True jika berhasil
        """
        if user_id not in self.admins:
            self.admins.append(user_id)
            self.save_users()
            logger.info(f"Added admin: {user_id}")
            return True
        return False
    
    def remove_admin(self, user_id: int) -> bool:
        """
        Hapus admin
        
        Args:
            user_id: ID pengguna Telegram
        
        Returns:
            bool: True jika berhasil
        """
        if user_id in self.admins:
            self.admins.remove(user_id)
            self.save_users()
            logger.info(f"Removed admin: {user_id}")
            return True
        return False
    
    def add_allowed_user(self, user_id: int) -> bool:
        """
        Tambahkan user yang diizinkan
        
        Args:
            user_id: ID pengguna Telegram
        
        Returns:
            bool: True jika berhasil
        """
        if user_id not in self.allowed_users:
            self.allowed_users.append(user_id)
            self.save_users()
            logger.info(f"Added allowed user: {user_id}")
            return True
        return False
    
    def remove_allowed_user(self, user_id: int) -> bool:
        """
        Hapus user dari daftar yang diizinkan
        
        Args:
            user_id: ID pengguna Telegram
        
        Returns:
            bool: True jika berhasil
        """
        if user_id in self.allowed_users:
            self.allowed_users.remove(user_id)
            self.save_users()
            logger.info(f"Removed allowed user: {user_id}")
            return True
        return False
    
    def get_admins(self) -> List[int]:
        """Dapatkan daftar admin"""
        return self.admins
    
    def get_allowed_users(self) -> List[int]:
        """Dapatkan daftar user yang diizinkan"""
        return self.allowed_users
    
    def get_user_status(self, user_id: int) -> Dict[str, bool]:
        """
        Dapatkan status user
        
        Args:
            user_id: ID pengguna Telegram
        
        Returns:
            dict: Status user (admin dan allowed)
        """
        return {
            'is_admin': self.is_admin(user_id),
            'is_allowed': self.is_allowed(user_id)
        } 