from .logger import user_action_logger


class LoggingMixin:
    """Миксин для добавления логирования в views"""
    
    def log_action(self, action, target=None, details=None, status='success'):
        """Логируем действие из view"""
        if hasattr(self, 'request'):
            user_action_logger.log_action(
                self.request, action, target, details, status
            )
    
    def log_create(self, object_id, object_name):
        """Логируем создание объекта"""
        model_name = self.model.__name__ if hasattr(self, 'model') else 'Object'
        self.log_action(
            f"CREATE {model_name}",
            target=f"{model_name}(ID:{object_id}, Name:{object_name})"
        )
    
    def log_update(self, object_id, object_name):
        """Логируем обновление объекта"""
        model_name = self.model.__name__ if hasattr(self, 'model') else 'Object'
        self.log_action(
            f"UPDATE {model_name}",
            target=f"{model_name}(ID:{object_id}, Name:{object_name})"
        )


class ViewAccessLoggingMixin:
    """Логирует факт посещения view, включая анонимных пользователей"""
    
    access_action = None
    
    def dispatch(self, request, *args, **kwargs):
        try:
            response = super().dispatch(request, *args, **kwargs)
        except Exception:
            self._log_view_access(request, kwargs, status='error')
            raise
        else:
            self._log_view_access(request, kwargs)
            return response
    
    def _log_view_access(self, request, view_kwargs, status='success'):
        action = self.access_action or self._derive_action_name()
        target = f"Path: {request.get_full_path()}"
        details = self._build_details(request, view_kwargs)
        user_action_logger.log_action(
            request,
            action,
            target=target,
            details=details,
            status=status
        )
    
    def _derive_action_name(self):
        if hasattr(self, 'model') and self.model:
            return f"VIEW {self.model.__name__}"
        return f"VIEW {self.__class__.__name__}"
    
    def _build_details(self, request, view_kwargs):
        details_parts = []
        
        if view_kwargs:
            details_parts.append(f"kwargs={self._stringify_mapping(view_kwargs)}")
        
        if request.GET:
            details_parts.append(
                f"query={self._stringify_querydict(request.GET)}"
            )
        
        return " | ".join(details_parts) if details_parts else None
    
    def _stringify_mapping(self, mapping):
        return {key: self._stringify_value(value) for key, value in mapping.items()}
    
    def _stringify_querydict(self, querydict):
        serialized = {}
        for key, values in querydict.lists():
            if not values:
                serialized[key] = ''
            elif len(values) == 1:
                serialized[key] = self._stringify_value(values[0])
            else:
                serialized[key] = [self._stringify_value(value) for value in values]
        return serialized
    
    def _stringify_value(self, value):
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return str(value)