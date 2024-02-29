import logging

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a console handler and set the formatter
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(console_handler)
