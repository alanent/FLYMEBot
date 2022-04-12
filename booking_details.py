# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
class BookingDetails:
    def __init__(
        self,
        origin: str = None,
        destination: str = None,
        start_date: str = None,
        end_date: str = None,
        budget: str = None):

        self.origin = origin
        self.destination = destination
        self.start_date = start_date
        self.end_date = end_date
        self.budget = budget
