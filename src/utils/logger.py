import logging

def get_logger(name='app'):
    """
    Get or create a logger by name.
    Default name: 'app'
    """
    return logging.getLogger(name)
