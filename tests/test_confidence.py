from engine.confidence import ConfidenceCalculator


def test_confidence_normal_value():

    calculator = ConfidenceCalculator()

    result = calculator.calculate(0.75)

    assert result == 0.75


def test_confidence_lower_bound():

    calculator = ConfidenceCalculator()

    result = calculator.calculate(-0.5)

    assert result == 0.0


def test_confidence_upper_bound():

    calculator = ConfidenceCalculator()

    result = calculator.calculate(1.5)

    assert result == 1.0


def test_confidence_high():

    calculator = ConfidenceCalculator()

    assert calculator.classify(0.90) == "HIGH"


def test_confidence_medium():

    calculator = ConfidenceCalculator()

    assert calculator.classify(0.65) == "MEDIUM"


def test_confidence_low():

    calculator = ConfidenceCalculator()

    assert calculator.classify(0.30) == "LOW"