from engine.root_cause_engine import RootCauseEngine


def test_root_cause_engine_detects_cpu_memory_resource_pressure():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "CPU_MEMORY",
            "strength": "HIGH",
            "message": "CPU and memory pressure are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1

    assert result[0]["category"] == "SYSTEM"

    assert result[0]["severity"] == "WARNING"

    assert (
        result[0]["message"]
        == "CPU and memory resource pressure may be contributing to system performance degradation."
    )

def test_root_cause_engine_detects_cpu_process_resource_pressure():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "CPU_PROCESS",
            "strength": "HIGH",
            "message": "CPU usage and process activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1

    assert result[0]["category"] == "PROCESS"

    assert result[0]["severity"] == "WARNING"

    assert (
        result[0]["message"]
        == "A process may be contributing to excessive CPU usage and system performance degradation."
    )

def test_root_cause_engine_detects_multiple_root_causes():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "CPU_MEMORY",
            "strength": "HIGH",
            "message": "CPU and memory pressure are correlated."
        },
        {
            "type": "CPU_PROCESS",
            "strength": "HIGH",
            "message": "CPU usage and process activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 2

    assert result[0]["category"] == "SYSTEM"
    assert result[0]["severity"] == "WARNING"

    assert result[1]["category"] == "PROCESS"
    assert result[1]["severity"] == "WARNING"

def test_root_cause_engine_detects_memory_process_pressure():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "MEMORY_PROCESS",
            "strength": "HIGH",
            "message": "Memory usage and process activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1

    assert result[0]["category"] == "PROCESS"

    assert result[0]["severity"] == "WARNING"

    assert (
        result[0]["message"]
        == "A process may be contributing to excessive memory usage and system performance degradation."
    )

def test_root_cause_engine_detects_three_root_causes():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "CPU_MEMORY",
            "strength": "HIGH",
            "message": "CPU and memory pressure are correlated."
        },
        {
            "type": "CPU_PROCESS",
            "strength": "HIGH",
            "message": "CPU usage and process activity are correlated."
        },
        {
            "type": "MEMORY_PROCESS",
            "strength": "HIGH",
            "message": "Memory usage and process activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 3

    assert result[0]["category"] == "SYSTEM"
    assert result[0]["severity"] == "WARNING"

    assert result[1]["category"] == "PROCESS"
    assert result[1]["severity"] == "WARNING"

    assert result[2]["category"] == "PROCESS"
    assert result[2]["severity"] == "WARNING"

def test_root_cause_engine_detects_memory_storage_pressure():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "MEMORY_STORAGE",
            "strength": "HIGH",
            "message": "Memory pressure and storage activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1

    assert result[0]["category"] == "MEMORY"

    assert result[0]["severity"] == "WARNING"

    assert (
        result[0]["message"]
        == "Memory pressure may be causing increased storage activity and system performance degradation."
    )

def test_root_cause_engine_detects_four_root_causes():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "CPU_MEMORY",
            "strength": "HIGH",
            "message": "CPU and memory pressure are correlated."
        },
        {
            "type": "CPU_PROCESS",
            "strength": "HIGH",
            "message": "CPU usage and process activity are correlated."
        },
        {
            "type": "MEMORY_PROCESS",
            "strength": "HIGH",
            "message": "Memory usage and process activity are correlated."
        },
        {
            "type": "MEMORY_STORAGE",
            "strength": "HIGH",
            "message": "Memory pressure and storage activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 4

    assert result[0]["category"] == "SYSTEM"
    assert result[0]["severity"] == "WARNING"

    assert result[1]["category"] == "PROCESS"
    assert result[1]["severity"] == "WARNING"

    assert result[2]["category"] == "PROCESS"
    assert result[2]["severity"] == "WARNING"

    assert result[3]["category"] == "MEMORY"
    assert result[3]["severity"] == "WARNING"

def test_root_cause_engine_detects_cpu_storage_pressure():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "CPU_STORAGE",
            "strength": "HIGH",
            "message": "CPU pressure and storage activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1

    assert result[0]["category"] == "STORAGE"

    assert result[0]["severity"] == "WARNING"

    assert (
        result[0]["message"]
        == "CPU pressure may be associated with increased storage activity and system performance degradation."
    )

def test_root_cause_engine_detects_five_root_causes():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "CPU_MEMORY",
            "strength": "HIGH",
            "message": "CPU and memory pressure are correlated."
        },
        {
            "type": "CPU_PROCESS",
            "strength": "HIGH",
            "message": "CPU usage and process activity are correlated."
        },
        {
            "type": "MEMORY_PROCESS",
            "strength": "HIGH",
            "message": "Memory usage and process activity are correlated."
        },
        {
            "type": "MEMORY_STORAGE",
            "strength": "HIGH",
            "message": "Memory pressure and storage activity are correlated."
        },
        {
            "type": "CPU_STORAGE",
            "strength": "HIGH",
            "message": "CPU pressure and storage activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 5

    assert result[0]["category"] == "SYSTEM"
    assert result[0]["severity"] == "WARNING"

    assert result[1]["category"] == "PROCESS"
    assert result[1]["severity"] == "WARNING"

    assert result[2]["category"] == "PROCESS"
    assert result[2]["severity"] == "WARNING"

    assert result[3]["category"] == "MEMORY"
    assert result[3]["severity"] == "WARNING"

    assert result[4]["category"] == "STORAGE"
    assert result[4]["severity"] == "WARNING"

def test_root_cause_engine_detects_cpu_network_pressure():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "CPU_NETWORK",
            "strength": "HIGH",
            "message": "CPU pressure and network activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1

    assert result[0]["category"] == "NETWORK"

    assert result[0]["severity"] == "WARNING"

    assert (
        result[0]["message"]
        == "CPU pressure may be associated with network activity and system performance degradation."
    )

def test_root_cause_engine_detects_memory_network_pressure():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "MEMORY_NETWORK",
            "strength": "HIGH",
            "message": "Memory pressure and network activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1

    assert result[0]["category"] == "NETWORK"

    assert result[0]["severity"] == "WARNING"

    assert (
        result[0]["message"]
        == "Memory pressure may be associated with network activity and system performance degradation."
    )

def test_root_cause_engine_detects_storage_network_pressure():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "STORAGE_NETWORK",
            "strength": "HIGH",
            "message": "Storage pressure and network activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1

    assert result[0]["category"] == "STORAGE"

    assert result[0]["severity"] == "WARNING"

    assert (
        result[0]["message"]
        == "Storage pressure may be associated with network activity and system performance degradation."
    )

def test_root_cause_engine_detects_network_process_pressure():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "NETWORK_PROCESS",
            "strength": "HIGH",
            "message": "Network activity and process activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1

    assert result[0]["category"] == "PROCESS"

    assert result[0]["severity"] == "WARNING"

    assert (
        result[0]["message"]
        == "A process may be contributing to network activity and system performance degradation."
    )

def test_root_cause_engine_detects_all_supported_correlations():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "CPU_MEMORY",
            "strength": "HIGH",
            "message": "CPU and memory pressure are correlated."
        },
        {
            "type": "CPU_PROCESS",
            "strength": "HIGH",
            "message": "CPU usage and process activity are correlated."
        },
        {
            "type": "MEMORY_PROCESS",
            "strength": "HIGH",
            "message": "Memory usage and process activity are correlated."
        },
        {
            "type": "MEMORY_STORAGE",
            "strength": "HIGH",
            "message": "Memory pressure and storage activity are correlated."
        },
        {
            "type": "CPU_STORAGE",
            "strength": "HIGH",
            "message": "CPU pressure and storage activity are correlated."
        },
        {
            "type": "CPU_NETWORK",
            "strength": "HIGH",
            "message": "CPU pressure and network activity are correlated."
        },
        {
            "type": "MEMORY_NETWORK",
            "strength": "HIGH",
            "message": "Memory pressure and network activity are correlated."
        },
        {
            "type": "STORAGE_NETWORK",
            "strength": "HIGH",
            "message": "Storage pressure and network activity are correlated."
        },
        {
            "type": "NETWORK_PROCESS",
            "strength": "HIGH",
            "message": "Network activity and process activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 9

    categories = [root_cause["category"] for root_cause in result]

    assert categories == [
        "SYSTEM",
        "PROCESS",
        "PROCESS",
        "MEMORY",
        "STORAGE",
        "NETWORK",
        "NETWORK",
        "STORAGE",
        "PROCESS",
    ]

    assert all(
        root_cause["severity"] == "WARNING"
        for root_cause in result
    )

def test_root_cause_engine_ignores_unknown_correlation():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "UNKNOWN_CORRELATION",
            "strength": "HIGH",
            "message": "Unknown correlation."
        }
    ]

    result = engine.analyze(correlations)

    assert result == []

def test_root_cause_engine_detects_medium_cpu_memory_correlation():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "CPU_MEMORY",
            "strength": "MEDIUM",
            "message": "CPU and memory pressure are moderately correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1
    assert result[0]["category"] == "SYSTEM"
    assert result[0]["severity"] == "WARNING"
    assert result[0]["priority"] == 1
    assert result[0]["confidence"] == "MEDIUM"

def test_root_cause_engine_assigns_priority_to_cpu_memory_root_cause():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "CPU_MEMORY",
            "strength": "HIGH",
            "message": "CPU and memory pressure are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1

    assert result[0]["priority"] == 1

def test_root_cause_engine_assigns_lower_priority_to_cpu_process_root_cause():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "CPU_PROCESS",
            "strength": "HIGH",
            "message": "CPU usage and process activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1

    assert result[0]["priority"] == 2

def test_root_cause_engine_assigns_priority_to_memory_process_root_cause():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "MEMORY_PROCESS",
            "strength": "HIGH",
            "message": "Memory usage and process activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1

    assert result[0]["priority"] == 3

def test_root_cause_engine_assigns_priority_to_memory_storage_root_cause():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "MEMORY_STORAGE",
            "strength": "HIGH",
            "message": "Memory pressure and storage activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1

    assert result[0]["priority"] == 4

def test_root_cause_engine_assigns_priority_to_cpu_storage_root_cause():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "CPU_STORAGE",
            "strength": "HIGH",
            "message": "CPU pressure and storage activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1

    assert result[0]["priority"] == 5

def test_root_cause_engine_assigns_priority_to_cpu_network_root_cause():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "CPU_NETWORK",
            "strength": "HIGH",
            "message": "CPU pressure and network activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1

    assert result[0]["priority"] == 6

def test_root_cause_engine_assigns_priority_to_memory_network_root_cause():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "MEMORY_NETWORK",
            "strength": "HIGH",
            "message": "Memory pressure and network activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1

    assert result[0]["priority"] == 7

def test_root_cause_engine_assigns_priority_to_storage_network_root_cause():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "STORAGE_NETWORK",
            "strength": "HIGH",
            "message": "Storage pressure and network activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1

    assert result[0]["priority"] == 8

def test_root_cause_engine_assigns_priority_to_network_process_root_cause():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "NETWORK_PROCESS",
            "strength": "HIGH",
            "message": "Network activity and process activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1

    assert result[0]["priority"] == 9

def test_root_cause_engine_orders_root_causes_by_priority():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "CPU_STORAGE",
            "strength": "HIGH",
            "message": "CPU pressure and storage activity are correlated."
        },
        {
            "type": "NETWORK_PROCESS",
            "strength": "HIGH",
            "message": "Network activity and process activity are correlated."
        },
        {
            "type": "CPU_MEMORY",
            "strength": "HIGH",
            "message": "CPU and memory pressure are correlated."
        },
        {
            "type": "CPU_PROCESS",
            "strength": "HIGH",
            "message": "CPU usage and process activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    priorities = [
        root_cause["priority"]
        for root_cause in result
    ]

    assert priorities == [1, 2, 5, 9]

def test_root_cause_engine_orders_all_root_causes_by_priority():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "NETWORK_PROCESS",
            "strength": "HIGH",
            "message": "Network activity and process activity are correlated."
        },
        {
            "type": "MEMORY_STORAGE",
            "strength": "HIGH",
            "message": "Memory pressure and storage activity are correlated."
        },
        {
            "type": "CPU_NETWORK",
            "strength": "HIGH",
            "message": "CPU pressure and network activity are correlated."
        },
        {
            "type": "CPU_MEMORY",
            "strength": "HIGH",
            "message": "CPU and memory pressure are correlated."
        },
        {
            "type": "STORAGE_NETWORK",
            "strength": "HIGH",
            "message": "Storage pressure and network activity are correlated."
        },
        {
            "type": "MEMORY_NETWORK",
            "strength": "HIGH",
            "message": "Memory pressure and network activity are correlated."
        },
        {
            "type": "CPU_STORAGE",
            "strength": "HIGH",
            "message": "CPU pressure and storage activity are correlated."
        },
        {
            "type": "MEMORY_PROCESS",
            "strength": "HIGH",
            "message": "Memory usage and process activity are correlated."
        },
        {
            "type": "CPU_PROCESS",
            "strength": "HIGH",
            "message": "CPU usage and process activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    priorities = [
        root_cause["priority"]
        for root_cause in result
    ]

    assert priorities == [1, 2, 3, 4, 5, 6, 7, 8, 9]

def test_root_cause_engine_deduplicates_root_causes():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "CPU_MEMORY",
            "strength": "HIGH",
            "message": "CPU and memory pressure are correlated."
        },
        {
            "type": "CPU_MEMORY",
            "strength": "HIGH",
            "message": "CPU and memory pressure are correlated."
        },
        {
            "type": "CPU_PROCESS",
            "strength": "HIGH",
            "message": "CPU usage and process activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 2

    assert result[0]["priority"] == 1
    assert result[1]["priority"] == 2

def test_root_cause_engine_preserves_distinct_root_causes():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "CPU_MEMORY",
            "strength": "HIGH",
            "message": "CPU and memory pressure are correlated."
        },
        {
            "type": "CPU_PROCESS",
            "strength": "HIGH",
            "message": "CPU usage and process activity are correlated."
        },
        {
            "type": "MEMORY_PROCESS",
            "strength": "HIGH",
            "message": "Memory usage and process activity are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 3

    assert [root_cause["priority"] for root_cause in result] == [1, 2, 3]

def test_root_cause_engine_assigns_high_confidence_to_cpu_memory_root_cause():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "CPU_MEMORY",
            "strength": "HIGH",
            "message": "CPU and memory pressure are correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1
    assert result[0]["confidence"] == "HIGH"

def test_root_cause_engine_assigns_medium_confidence_to_medium_cpu_memory_correlation():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "CPU_MEMORY",
            "strength": "MEDIUM",
            "message": "CPU and memory pressure may be correlated."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1
    assert result[0]["confidence"] == "MEDIUM"

def test_root_cause_engine_assigns_low_confidence_to_low_cpu_memory_correlation():

    engine = RootCauseEngine()

    correlations = [
        {
            "type": "CPU_MEMORY",
            "strength": "LOW",
            "message": "CPU and memory pressure have a weak correlation."
        }
    ]

    result = engine.analyze(correlations)

    assert len(result) == 1
    assert result[0]["confidence"] == "LOW"
