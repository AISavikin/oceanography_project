import logging
import os
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

class UserActionLogger:
    """Логгер действий пользователей"""
    
    def __init__(self):
        self.logger = logging.getLogger('user_actions')
        
        # Создаем папку для логов если её нет
        log_dir = os.path.join(settings.BASE_DIR, 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file = os.path.join(log_dir, 'user_actions.log')
        
        # Настраиваем обработчик файла
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.setLevel(logging.INFO)
    
    def _get_user_info(self, request):
        """Получаем информацию о пользователе"""
        if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            return f"{request.user.username} (ID: {request.user.id})"
        else:
            return "Anonymous User"
    
    def _get_client_info(self, request):
        """Получаем информацию о клиенте"""
        ip = request.META.get('REMOTE_ADDR', 'Unknown IP')
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown Agent')
        return f"IP: {ip}, Agent: {user_agent[:100]}..."
    
    def log_action(self, request, action, target=None, details=None, status='success'):
        """Логируем действие пользователя"""
        user_info = self._get_user_info(request)
        client_info = self._get_client_info(request)
        
        log_message = f"USER: {user_info} | ACTION: {action}"
        
        if target:
            log_message += f" | TARGET: {target}"
        if details:
            log_message += f" | DETAILS: {details}"
        
        log_message += f" | STATUS: {status} | {client_info}"
        
        if status == 'error':
            self.logger.error(log_message)
        else:
            self.logger.info(log_message)
    
    # Специализированные методы для частых действий
    def log_create(self, request, model_name, object_id, object_name):
        self.log_action(
            request, 
            f"CREATE {model_name}",
            target=f"{model_name}(ID:{object_id}, Name:{object_name})",
            details=f"Created new {model_name}"
        )
    
    def log_update(self, request, model_name, object_id, object_name):
        self.log_action(
            request,
            f"UPDATE {model_name}", 
            target=f"{model_name}(ID:{object_id}, Name:{object_name})",
            details=f"Updated {model_name}"
        )
    
    def log_delete(self, request, model_name, object_id, object_name):
        self.log_action(
            request,
            f"DELETE {model_name}",
            target=f"{model_name}(ID:{object_id}, Name:{object_name})",
            details=f"Deleted {model_name}"
        )
    
    def log_upload(self, request, file_type, file_name, records_count=0):
        self.log_action(
            request,
            f"UPLOAD {file_type}",
            target=f"File: {file_name}",
            details=f"Records processed: {records_count}"
        )
    
    def log_login(self, request):
        self.log_action(request, "LOGIN", details="User logged in")
    
    def log_logout(self, request):
        self.log_action(request, "LOGOUT", details="User logged out")
    
    def log_error(self, request, action, error_message):
        self.log_action(
            request, 
            action, 
            status='error',
            details=f"Error: {error_message}"
        )

# Создаем глобальный экземпляр логгера
user_action_logger = UserActionLogger()