# -- encoding: UTF-8 --
from django.core.exceptions import ValidationError
from django.forms import BaseForm
from django.utils.translation import ugettext_lazy
from enumfields import Enum, EnumField
from enumfields.fields import freeze_enum, unfreeze_enum
import pytest
import six
from six import u


class Color(Enum):
    __order__ = 'RED GREEN BLUE'

    RED = 'r'
    GREEN = 'g'
    BLUE = 'b'

    class Labels:
        RED = 'Reddish'
        BLUE = ugettext_lazy(u('bluë'))


def test_choice_ordering():
    EXPECTED_CHOICES = (
        ('r', 'Reddish'),
        ('g', 'Green'),
        ('b', u('bluë')),
    )
    for ((ex_key, ex_val), (key, val)) in zip(EXPECTED_CHOICES, Color.choices()):
        assert key == ex_key
        assert six.text_type(val) == six.text_type(ex_val)

def test_custom_labels():
    # Custom label
    assert Color.RED.label == 'Reddish'
    assert six.text_type(Color.RED) == 'Reddish'

def test_automatic_labels():
    # Automatic label
    assert Color.GREEN.label == 'Green'
    assert six.text_type(Color.GREEN) == 'Green'

def test_lazy_labels():
    # Lazy label
    assert isinstance(six.text_type(Color.BLUE), six.string_types)
    assert six.text_type(Color.BLUE) == u('bluë')

def test_formfield_labels():
    # Formfield choice label
    form_field = EnumField(Color).formfield()
    expectations = dict((val.value, six.text_type(val)) for val in Color)
    for value, text in form_field.choices:
        if value:
            assert text == expectations[value]

def test_formfield_functionality():
    form_cls = type("FauxForm", (BaseForm,), {
        "base_fields": {"color": EnumField(Color).formfield()}
    })
    form = form_cls(data={"color": "r"})
    assert not form.errors
    assert form.cleaned_data["color"] == Color.RED

def test_invalid_to_python_fails():
    with pytest.raises(ValidationError) as ve:
        EnumField(Color).to_python("invalid")
    assert ve.value.code == "invalid_enum_value"

def test_import_by_string():
    assert EnumField("tests.test_enums.Color").enum == Color

def test_enum_freeze():
    frozen_enum = freeze_enum(Color)
    assert isinstance(frozen_enum, tuple)
    assert len(frozen_enum) == 3

    module_name, class_name, choices = frozen_enum
    assert module_name == 'tests.test_enums'
    assert class_name == 'Color'
    assert set(choices) == set((choice.name, choice.value) for choice in Color)

def test_enum_unfreeze_from_tuple():
    frozen_enum = (
        'tests.test_enums',
        'Color',
        (('RED', 'r'), ('GREEN', 'g'), ('BLUE', 'b')),
    )

    Color = unfreeze_enum(frozen_enum)
    assert Color.__name__ == 'Color'
    assert Color.__module__ == 'tests.test_enums'
    assert Color.RED.value == 'r'
    assert Color.GREEN.value == 'g'
    assert Color.BLUE.value == 'b'

def test_enum_unfreeze_from_str():
    frozen_enum = repr((
        'tests.test_enums',
        'Color',
        (('RED', 'r'), ('GREEN', 'g'), ('BLUE', 'b')),
    ))

    Color = unfreeze_enum(frozen_enum)
    assert Color.__name__ == 'Color'
    assert Color.__module__ == 'tests.test_enums'
    assert Color.RED.value == 'r'
    assert Color.GREEN.value == 'g'
    assert Color.BLUE.value == 'b'
