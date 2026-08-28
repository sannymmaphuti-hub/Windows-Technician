# ==========================================
# WINDOWS TECHNICIAN v0.2
# CENTRAL DIAGNOSTIC RULES
# ==========================================


# ------------------------------------------
# MEMORY THRESHOLDS
# ------------------------------------------

def get_memory_status(usage_percent):

    if usage_percent >= 95:
        return "CRITICAL"

    elif usage_percent >= 90:
        return "HIGH MEMORY PRESSURE"

    elif usage_percent >= 80:
        return "WARNING"

    elif usage_percent >= 70:
        return "ATTENTION"

    else:
        return "NORMAL"


# ------------------------------------------
# CPU THRESHOLDS
# ------------------------------------------

def get_cpu_status(usage_percent):

    if usage_percent >= 95:
        return "CRITICAL"

    elif usage_percent >= 85:
        return "WARNING"

    elif usage_percent >= 70:
        return "ATTENTION"

    else:
        return "NORMAL"


# ------------------------------------------
# STORAGE THRESHOLDS
# ------------------------------------------

def get_storage_status(usage_percent):

    if usage_percent >= 95:
        return "CRITICAL"

    elif usage_percent >= 90:
        return "WARNING"

    elif usage_percent >= 80:
        return "ATTENTION"

    else:
        return "HEALTHY"
