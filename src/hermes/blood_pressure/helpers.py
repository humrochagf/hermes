from hermes.blood_pressure.models import BloodLevel


def level_to_color(value: BloodLevel) -> str:
    match value:
        case BloodLevel.low:
            return "blue"
        case BloodLevel.normal:
            return "black"
        case BloodLevel.high:
            return "orange"
        case BloodLevel.danger:
            return "red"
