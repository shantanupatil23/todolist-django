"""
Views for the task APIs.
"""

from rest_framework import viewsets, mixins

from core.models import Task

from task import serializers

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class TaskViewSet(viewsets.ModelViewSet):
    """View for manage task APIs."""
    queryset = Task.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve tasks for authenticated user."""
        queryset = self.queryset
        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

    def get_serializer_class(self):
        """Return the serializer class for request."""
        return serializers.TaskSerializer

    def perform_create(self, serializer):
        """Create a new task."""
        serializer.save(user=self.request.user)


class BaseTaskAttrViewSet(
                mixins.DestroyModelMixin,
                mixins.UpdateModelMixin,
                mixins.ListModelMixin,
                viewsets.GenericViewSet):
    """Base viewset for task attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(task_isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()
