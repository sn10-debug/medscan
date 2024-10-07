class JobStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    CHOICES = (
        (PENDING, "Pending"),
        (PROCESSING, "Processing"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
        (CANCELLED, "Cancelled"),
    )


LINE_NAME_MAP = {
    "C0": "Control Line",
    "T1": "Test Line 1",
    "T2": "Test Line 2",
}


def get_activation_alias_schema():
    ACTIVATION_ALIAS_SCHEMA = {
        "type": "array",
        "title": "Activations",
        "maxItems": 3,
        "minItems": 0,
        "items": {
            "type": "object",
            "title": "Alias Map",
            "keys": {
                "activation": {
                    "type": "string",
                    "choices": list(LINE_NAME_MAP.values()),
                },
                "alias": {"type": "string"},
            },
        },
    }
    return ACTIVATION_ALIAS_SCHEMA
