import json
from datetime import datetime, date
from decimal import Decimal


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling datetime, date, and decimal objects."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)
