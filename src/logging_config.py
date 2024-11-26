import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    # Create a formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Set up logging for development
    if app.config['ENV'] == 'development':
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        app.logger.addHandler(console_handler)
        app.logger.setLevel(logging.DEBUG)
    else:  # Set up logging for production
        file_handler = RotatingFileHandler(
            'app.log', maxBytes=1024 * 1024 * 10, backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
