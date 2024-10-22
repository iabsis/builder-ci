import logging
from functools import wraps
from functools import wraps
from io import StringIO as StringBuffer

logger = logging.getLogger(__name__)

# Create the decorator
def capture_logs(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Create a new list to store logs for this method
        log_capture_string = StringBuffer()
        ch = logging.StreamHandler(log_capture_string)
        ch.setLevel(logging.DEBUG)
        logger.addHandler(ch)
        formatter = logging.Formatter('- %(message)s')
        ch.setFormatter(formatter)

        logger.warning("BLA")

        
        try:
            # Execute the decorated function
            result = func(self, *args, **kwargs)
            pass
        finally:
            # Remove the handler after the function execution
            self.logs = log_capture_string.getvalue()
            log_capture_string.close()

        #return result
    return wrapper

# Example class using the decorator
class MyClass:
    def __init__(self):
        self.logs = []

    @capture_logs
    def my_function(self):
        logging.info('This is an info message')
        logging.warning('This is a warning message')
        logging.error('This is an error message')

# Usage
my_object = MyClass()
my_object.my_function()

# Now the logs are stored in the object's logs attribute
print("Captured Logs:")
print(my_object.logs)
