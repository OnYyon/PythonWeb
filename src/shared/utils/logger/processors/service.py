def add_service(name: str):
    "Processor for add service name in log"

    def processor(logger, method_name, event_dict):
        event_dict["service"] = name
        return event_dict

    return processor
