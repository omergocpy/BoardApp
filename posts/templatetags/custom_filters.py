from django import template

register = template.Library()

# `endswith` filtresi, bir stringin belirtilen bir son ekle bitip bitmediğini kontrol eder.
@register.filter(name='endswith')
def endswith(value, suffix):
    return value.endswith(suffix)

# `length_is` filtresi, bir dizinin uzunluğunun belirli bir sayıya eşit olup olmadığını kontrol eder.
@register.filter
def length_is(value, arg):
    return len(value) == int(arg)

# `to_int` filtresi, bir değeri tam sayıya dönüştürmeye çalışır.
@register.filter
def to_int(value):
    """Convert a value to an integer."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

@register.filter(name='int')
def force_int(value):
    """String veya float gibi değerleri int'e çevirir."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def has_second_survey_due(user):
    """Kullanıcının ikinci anket zamanı geldi mi kontrol eder"""
    try:
        return user.survey_completion.is_second_survey_due()
    except:
        return False