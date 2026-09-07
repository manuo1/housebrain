from core.choices import LoadSheddingImportance


def test_choices_values_unchanged():
    """Frozen contract: Radiator.Importance and equipment.WaterHeater.importance
    both rely on these exact (value, label) pairs staying stable — changing
    them would need a migration on both models."""
    assert LoadSheddingImportance.choices == [
        (0, "Critique"),
        (1, "Haute"),
        (2, "Moyenne"),
        (3, "Basse"),
    ]
