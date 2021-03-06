"""ESI-bot channel helper class."""


import os
import time

from esi_bot.utils import paginated_id_to_names


class Channels(object):
    """Join and store channel IDs -> names."""

    def __init__(self, slack):
        self._slack = slack
        self._channels = {}  # {id: name}
        self._last_sync = 0
        self._allowed = os.environ.get("BOT_CHANNELS", "esi").split(",")
        self._joined = {}  # {id: name}
        self.primary = None  # primary channel ID
        self.update_names()

    def update_names(self):
        """Updates our names cache once per minute at max."""

        if time.time() - self._last_sync < 60:
            return

        self._last_sync = time.time()
        channels = paginated_id_to_names(
            self._slack,
            "channels.list",
            "channels",
            exclude_archived=1,
        )
        if channels:
            self._channels = channels

    def enter_channels(self):
        """Attempts to join the permitted channels.

        Returns:
            boolean of any channel succesfully joined
        """

        for ch_id, ch_name in self._channels.items():
            if ch_name in self._allowed:
                join = self._slack.api_call("channels.join", channel=ch_id)
                if join["ok"]:
                    if self.primary is None:
                        self.primary = ch_id
                    self._joined[ch_id] = ch_name
                else:
                    self._joined.pop(ch_id, None)

        return self.primary is not None

    def get_name(self, channel_id):
        """Returns the channel name if we're in it."""

        return self._joined.get(channel_id)
