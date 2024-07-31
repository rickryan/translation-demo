import logging

def configure_logging(level=logging.DEBUG):
    """
    Configure the logging with a specific level.
    """
    logging.basicConfig(level=level,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def set_logger_level(level_name):
    """
    Set the logging level by name (e.g., 'DEBUG', 'INFO').
    """
    level = getattr(logging, level_name.upper(), None)
    if not isinstance(level, int):
        raise ValueError(f'Invalid log level: {level_name}')
    logging.getLogger().setLevel(level)
    
