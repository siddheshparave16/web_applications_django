import time
import logging

logger = logging.getLogger(__name__)

class RequestTimeMiddleware:

    def __init__(self, get_responce):
        self.get_responce = get_responce

    def __call__(self, request):
        # start time wheen request is received
        start_time = time.time()

        # process the request and get the responce
        response = self.get_responce(request)

        # Calculate the time taken to process the request
        duration = time.time() - start_time

        # log the time taken
        logger.info(f"Request to {request.path} took {duration:.2f} seconds.")

        return response
