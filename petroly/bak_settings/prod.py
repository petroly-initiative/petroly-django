import os
import re

import dj_database_url

from .base import *

# For Discord notification
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", default="")




