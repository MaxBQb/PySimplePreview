import examples.example.simple
from examples.example.condition_import import preview


@preview
def preview3():
    return examples.example.simple.get_layout("Derived")
