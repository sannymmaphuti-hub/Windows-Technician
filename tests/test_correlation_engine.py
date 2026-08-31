from engine.correlation_engine import CorrelationEngine


def test_correlation_engine_returns_empty_list_when_no_evidence():
    engine = CorrelationEngine()

    result = engine.analyze({})

    assert result == []

def test_correlation_engine_detects_cpu_memory_pressure():
    engine = CorrelationEngine()

    evidence = {
        "CPU": {
            "usage_percent": 90
        },
        "Memory": {
            "usage_percent": 88
        }
    }

    result = engine.analyze(evidence)

    assert len(result) == 1

    correlation = result[0]

    assert correlation["type"] == "CPU_MEMORY"
    assert correlation["strength"] == "HIGH"

def test_correlation_engine_does_not_correlate_cpu_without_memory_pressure():
    engine = CorrelationEngine()

    evidence = {
        "CPU": {
            "usage_percent": 90
        },
        "Memory": {
            "usage_percent": 60
        }
    }

    result = engine.analyze(evidence)

    assert result == []

def test_correlation_engine_does_not_correlate_memory_without_cpu_pressure():
    engine = CorrelationEngine()

    evidence = {
        "CPU": {
            "usage_percent": 60
        },
        "Memory": {
            "usage_percent": 90
        }
    }

    result = engine.analyze(evidence)

    assert result == []

def test_correlation_engine_detects_critical_cpu_memory_pressure():
    engine = CorrelationEngine()

    evidence = {
        "CPU": {
            "usage_percent": 98
        },
        "Memory": {
            "usage_percent": 97
        }
    }

    result = engine.analyze(evidence)

    assert len(result) == 1

    correlation = result[0]

    assert correlation["type"] == "CPU_MEMORY"
    assert correlation["strength"] == "CRITICAL"

def test_correlation_engine_handles_missing_cpu_data():
    engine = CorrelationEngine()

    evidence = {
        "Memory": {
            "usage_percent": 90
        }
    }

    result = engine.analyze(evidence)

    assert result == []

def test_correlation_engine_handles_missing_memory_data():
    engine = CorrelationEngine()

    evidence = {
        "CPU": {
            "usage_percent": 90
        }
    }

    result = engine.analyze(evidence)

    assert result == []

def test_correlation_engine_detects_cpu_process_correlation():
    engine = CorrelationEngine()

    evidence = {
        "CPU": {
            "usage_percent": 92
        },
        "Processes": {
            "top_process": "chrome.exe",
            "top_process_cpu_percent": 75
        }
    }

    result = engine.analyze(evidence)

    assert len(result) == 1

    correlation = result[0]

    assert correlation["type"] == "CPU_PROCESS"
    assert correlation["strength"] == "HIGH"

def test_correlation_engine_does_not_correlate_memory_with_low_process_memory_usage():
    engine = CorrelationEngine()

    evidence = {
        "Memory": {
            "usage_percent": 92
        },
        "Processes": {
            "top_process": "chrome.exe",
            "top_process_memory_percent": 40
        }
    }

    result = engine.analyze(evidence)

    assert result == []

def test_correlation_engine_handles_missing_process_data():
    engine = CorrelationEngine()

    evidence = {
        "CPU": {
            "usage_percent": 92
        }
    }

    result = engine.analyze(evidence)

    assert result == []

def test_correlation_engine_detects_critical_cpu_process_correlation():
    engine = CorrelationEngine()

    evidence = {
        "CPU": {
            "usage_percent": 97
        },
        "Processes": {
            "top_process": "chrome.exe",
            "top_process_cpu_percent": 92
        }
    }

    result = engine.analyze(evidence)

    assert len(result) == 1

    correlation = result[0]

    assert correlation["type"] == "CPU_PROCESS"
    assert correlation["strength"] == "CRITICAL"

def test_correlation_engine_keeps_cpu_process_correlation_high_below_critical_process_threshold():
    engine = CorrelationEngine()

    evidence = {
        "CPU": {
            "usage_percent": 95
        },
        "Processes": {
            "top_process": "chrome.exe",
            "top_process_cpu_percent": 89
        }
    }

    result = engine.analyze(evidence)

    assert len(result) == 1

    correlation = result[0]

    assert correlation["type"] == "CPU_PROCESS"
    assert correlation["strength"] == "HIGH"

def test_correlation_engine_detects_memory_process_correlation():
    engine = CorrelationEngine()

    evidence = {
        "Memory": {
            "usage_percent": 92
        },
        "Processes": {
            "top_process": "chrome.exe",
            "top_process_memory_percent": 80
        }
    }

    result = engine.analyze(evidence)

    assert len(result) == 1

    correlation = result[0]

    assert correlation["type"] == "MEMORY_PROCESS"
    assert correlation["strength"] == "HIGH"

def test_correlation_engine_detects_memory_storage_correlation():
    engine = CorrelationEngine()

    evidence = {
        "Memory": {
            "usage_percent": 92
        },
        "Storage": {
            "usage_percent": 95
        }
    }

    result = engine.analyze(evidence)

    assert len(result) == 1

    correlation = result[0]

    assert correlation["type"] == "MEMORY_STORAGE"
    assert correlation["strength"] == "HIGH"

def test_correlation_engine_does_not_correlate_memory_with_low_storage_usage():
    engine = CorrelationEngine()

    evidence = {
        "Memory": {
            "usage_percent": 92
        },
        "Storage": {
            "usage_percent": 70
        }
    }

    result = engine.analyze(evidence)

    assert result == []

def test_correlation_engine_detects_critical_memory_storage_correlation():
    engine = CorrelationEngine()

    evidence = {
        "Memory": {
            "usage_percent": 97
        },
        "Storage": {
            "usage_percent": 98
        }
    }

    result = engine.analyze(evidence)

    assert len(result) == 1

    correlation = result[0]

    assert correlation["type"] == "MEMORY_STORAGE"
    assert correlation["strength"] == "CRITICAL"

def test_correlation_engine_detects_cpu_storage_correlation():
    engine = CorrelationEngine()

    evidence = {
        "CPU": {
            "usage_percent": 92
        },
        "Storage": {
            "usage_percent": 95
        }
    }

    result = engine.analyze(evidence)

    assert len(result) == 1

    correlation = result[0]

    assert correlation["type"] == "CPU_STORAGE"
    assert correlation["strength"] == "HIGH"

def test_correlation_engine_does_not_correlate_cpu_with_low_storage_usage():
    engine = CorrelationEngine()

    evidence = {
        "CPU": {
            "usage_percent": 92
        },
        "Storage": {
            "usage_percent": 70
        }
    }

    result = engine.analyze(evidence)

    assert result == []

def test_correlation_engine_detects_critical_cpu_storage_correlation():
    engine = CorrelationEngine()

    evidence = {
        "CPU": {
            "usage_percent": 97
        },
        "Storage": {
            "usage_percent": 98
        }
    }

    result = engine.analyze(evidence)

    assert len(result) == 1

    correlation = result[0]

    assert correlation["type"] == "CPU_STORAGE"
    assert correlation["strength"] == "CRITICAL"

def test_correlation_engine_keeps_cpu_storage_high_below_critical_storage_threshold():
    engine = CorrelationEngine()

    evidence = {
        "CPU": {
            "usage_percent": 95
        },
        "Storage": {
            "usage_percent": 94
        }
    }

    result = engine.analyze(evidence)

    assert len(result) == 1

    correlation = result[0]

    assert correlation["type"] == "CPU_STORAGE"
    assert correlation["strength"] == "HIGH"

def test_correlation_engine_detects_cpu_network_correlation():
    engine = CorrelationEngine()

    evidence = {
        "CPU": {
            "usage_percent": 92
        },
        "Network": {
            "activity_percent": 85
        }
    }

    result = engine.analyze(evidence)

    assert len(result) == 1

    correlation = result[0]

    assert correlation["type"] == "CPU_NETWORK"
    assert correlation["strength"] == "HIGH"

def test_correlation_engine_does_not_correlate_cpu_with_low_network_activity():
    engine = CorrelationEngine()

    evidence = {
        "CPU": {
            "usage_percent": 92
        },
        "Network": {
            "activity_percent": 40
        }
    }

    result = engine.analyze(evidence)

    assert result == []

def test_correlation_engine_detects_critical_cpu_network_correlation():
    engine = CorrelationEngine()

    evidence = {
        "CPU": {
            "usage_percent": 97
        },
        "Network": {
            "activity_percent": 92
        }
    }

    result = engine.analyze(evidence)

    assert len(result) == 1

    correlation = result[0]

    assert correlation["type"] == "CPU_NETWORK"
    assert correlation["strength"] == "CRITICAL"

def test_correlation_engine_keeps_cpu_network_high_below_critical_network_threshold():
    engine = CorrelationEngine()

    evidence = {
        "CPU": {
            "usage_percent": 95
        },
        "Network": {
            "activity_percent": 89
        }
    }

    result = engine.analyze(evidence)

    assert len(result) == 1

    correlation = result[0]

    assert correlation["type"] == "CPU_NETWORK"
    assert correlation["strength"] == "HIGH"

def test_correlation_engine_detects_memory_network_correlation():
    engine = CorrelationEngine()

    evidence = {
        "Memory": {
            "usage_percent": 92
        },
        "Network": {
            "activity_percent": 85
        }
    }

    result = engine.analyze(evidence)

    assert len(result) == 1

    correlation = result[0]

    assert correlation["type"] == "MEMORY_NETWORK"
    assert correlation["strength"] == "HIGH"

def test_correlation_engine_does_not_correlate_memory_with_low_network_activity():
    engine = CorrelationEngine()

    evidence = {
        "Memory": {
            "usage_percent": 92
        },
        "Network": {
            "activity_percent": 40
        }
    }

    result = engine.analyze(evidence)

    assert result == []

def test_correlation_engine_detects_critical_memory_network_correlation():
    engine = CorrelationEngine()

    evidence = {
        "Memory": {
            "usage_percent": 97
        },
        "Network": {
            "activity_percent": 92
        }
    }

    result = engine.analyze(evidence)

    assert len(result) == 1

    correlation = result[0]

    assert correlation["type"] == "MEMORY_NETWORK"
    assert correlation["strength"] == "CRITICAL"

def test_correlation_engine_keeps_memory_network_high_below_critical_network_threshold():
    engine = CorrelationEngine()

    evidence = {
        "Memory": {
            "usage_percent": 95
        },
        "Network": {
            "activity_percent": 89
        }
    }

    result = engine.analyze(evidence)

    assert len(result) == 1

    correlation = result[0]

    assert correlation["type"] == "MEMORY_NETWORK"
    assert correlation["strength"] == "HIGH"

def test_correlation_engine_detects_storage_network_correlation():
    engine = CorrelationEngine()

    evidence = {
        "Storage": {
            "usage_percent": 95
        },
        "Network": {
            "activity_percent": 85
        }
    }

    result = engine.analyze(evidence)

    assert len(result) == 1

    correlation = result[0]

    assert correlation["type"] == "STORAGE_NETWORK"
    assert correlation["strength"] == "HIGH"

def test_correlation_engine_detects_network_process_correlation():
    engine = CorrelationEngine()

    evidence = {
        "Network": {
            "activity_percent": 85
        },
        "Processes": {
            "top_process": "chrome.exe",
            "top_process_network_percent": 75
        }
    }

    result = engine.analyze(evidence)

    assert len(result) == 1

    correlation = result[0]

    assert correlation["type"] == "NETWORK_PROCESS"
    assert correlation["strength"] == "HIGH"
    assert "chrome.exe" in correlation["message"]

def test_correlation_engine_does_not_correlate_network_with_low_process_network_usage():
    engine = CorrelationEngine()

    evidence = {
        "Network": {
            "activity_percent": 92
        },
        "Processes": {
            "top_process": "chrome.exe",
            "top_process_network_percent": 40
        }
    }

    result = engine.analyze(evidence)

    assert result == []

def test_correlation_engine_detects_critical_network_process_correlation():
    engine = CorrelationEngine()

    evidence = {
        "Network": {
            "activity_percent": 97
        },
        "Processes": {
            "top_process": "chrome.exe",
            "top_process_network_percent": 92
        }
    }

    result = engine.analyze(evidence)

    assert len(result) == 1

    correlation = result[0]

    assert correlation["type"] == "NETWORK_PROCESS"
    assert correlation["strength"] == "CRITICAL"
    assert "chrome.exe" in correlation["message"]

def test_correlation_engine_keeps_network_process_high_below_critical_process_threshold():
    engine = CorrelationEngine()

    evidence = {
        "Network": {
            "activity_percent": 95
        },
        "Processes": {
            "top_process": "chrome.exe",
            "top_process_network_percent": 89
        }
    }

    result = engine.analyze(evidence)

    assert len(result) == 1

    correlation = result[0]

    assert correlation["type"] == "NETWORK_PROCESS"
    assert correlation["strength"] == "HIGH"
