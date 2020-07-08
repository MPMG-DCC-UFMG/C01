"""
This module contains classes which abstract the process of checking an entry's
existence
"""

# Allow postponed evaluation of type annotations
from __future__ import annotations

from .entry_probing_request import ProbingRequest
from .entry_probing_response import ProbingResponse


class EntryProbing():
    """
    General wrapper for both a ProbingRequest and a ProbingResponse. The
    check_entry method uses these handlers to check if a given entry in a
    website has been hit or not
    """

    def __init__(self, req_handler: ProbingRequest):
        """
        Initializes the class with the request handler

        :param req_handler: Handler describing how to execute the request
        """
        if not isinstance(req_handler, ProbingRequest):
            raise TypeError("Request handler must be a subclass of " +
                            "ProbingRequest")

        self.req_handler = req_handler
        self.resp_handlers = []


    def add_response_handler(self, resp_handler: ProbingResponse
                             ) -> EntryProbing:
        """
        Adds a response handler to the probing process

        :param resp_handler: Handler describing how to validate the response

        :returns: Entry probing object, to enable chaining
        """
        if not isinstance(resp_handler, ProbingResponse):
            raise TypeError("Response handler must be a subclass of " +
                            "ProbingResponse")

        self.resp_handlers.append(resp_handler)
        return self


    def check_entry(self) -> bool:
        """
        Uses the request and response handlers to check for an entry's existence

        :returns: True if entry is valid, False otherwise
        """

        response = self.req_handler.process()
        return all([h.process(response) for h in self.resp_handlers])
