def add_environment(env: str):
    """Processor for add env in log"""

    def processor(logger, method_name, event_dict):
        event_dict["env"] = env
        return event_dict

    return processor
