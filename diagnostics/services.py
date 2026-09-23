import psutil


def get_services_by_process():
    service_groups = {}

    for service in psutil.win_service_iter():
        try:
            name = service.name()
            display_name = service.display_name()
            status = service.status()
            pid = service.pid()

            if pid is None or pid == 0:
                continue

            if pid not in service_groups:
                service_groups[pid] = []

            service_groups[pid].append({
                "name": name,
                "display_name": display_name,
                "status": status
            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            FileNotFoundError,
            OSError
        ):
            continue

    return service_groups
