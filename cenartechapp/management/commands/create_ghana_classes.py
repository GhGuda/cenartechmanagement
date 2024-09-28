from django.core.management.base import BaseCommand
from cenartechapp.models import Class_Form

class Command(BaseCommand):
    help = 'Create Ghana curriculum classes from Nursery to Form 3'

    def handle(self, *args, **kwargs):
        create_classes()
        self.stdout.write(self.style.SUCCESS('Successfully created Ghana curriculum classes.'))

def create_classes():
    ghana_classes = [
        "Nursery One", "Nursery Two", 
        "Kindergarten One", "Kindergarten Two",
        "Class One", "Class Two", "Class Three", 
        "Class Four", "Class Five", "Class Six",
        "Form One", "Form Two", "Form Three", "Completed Class"
    ]

    for class_name in ghana_classes:
        if not Class_Form.objects.filter(name=class_name).exists():
            Class_Form.objects.create(name=class_name)
