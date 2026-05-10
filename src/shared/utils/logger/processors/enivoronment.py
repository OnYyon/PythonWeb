def add_environment(env: str):
    def processor(logger, method_name, event_dict):
        event_dict["env"] = env
        return event_dict

    return processor
