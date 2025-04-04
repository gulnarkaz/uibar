# apartments/permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Пользовательские права доступа:
    - Разрешает чтение всем (GET, HEAD, OPTIONS запросы).
    - Разрешает изменение/удаление только владельцу объекта.
    """

    def has_object_permission(self, request, view, obj):
        # Права на чтение разрешены для любого запроса,
        # поэтому мы всегда разрешаем GET, HEAD или OPTIONS запросы.
        if request.method in permissions.SAFE_METHODS: # SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')
            return True

        # Права на запись (POST не проверяется здесь, т.к. объекта еще нет)
        # PUT, PATCH, DELETE проверяются здесь.
        # Разрешаем только если пользователь, делающий запрос (request.user),
        # является владельцем объекта (obj.owner).
        # Важно: У объекта `obj` должно быть поле `owner`. В нашей модели Apartment оно есть.
        return obj.owner == request.user
    
class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Пользовательские права доступа:
    - Разрешает чтение всем (GET, HEAD, OPTIONS запросы).
    - Разрешает изменение/удаление только автору объекта.
    """
    def has_object_permission(self, request, view, obj):
        # Разрешаем чтение всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Права на запись разрешены только если пользователь является автором.
        # Важно: У объекта `obj` должно быть поле `author`. В нашей модели Review оно есть.
        return obj.author == request.user
