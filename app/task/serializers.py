"""
Serializers for task APIs
"""
from rest_framework import serializers

from core.models import Task


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for tasks."""

    class Meta:
        model = Task
        fields = ['id', 'title', 'description']
        read_only_fields = ['id']

    def create(self, validated_data):
        """Create a task."""
        task = Task.objects.create(**validated_data)

        return task

    def update(self, instance, validated_data):
        """Update task."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
