# -*- coding: utf-8 -*-
from marvinbot.utils import get_message
from marvinbot.plugins import Plugin
from marvinbot.handlers import CommonFilters, MessageHandler
from marvinbot.filters import RegexpFilter
import logging
import re

log = logging.getLogger(__name__)


class Substitutions(Plugin):
    def __init__(self):
        super(Substitutions, self).__init__('substitutions')

    def get_default_config(self):
        return {
            'short_name': self.name,
            'enabled': True,
            'pattern': r'^s/(?P<pattern>.+?)(?<!\\)/(?P<replacement>.*?)/?$'
        }

    def configure(self, config):
        self.plain_pattern = config.get('pattern')
        self.pattern = re.compile(config.get('pattern'))
        pass

    def setup_handlers(self, adapter):
        self.add_handler(MessageHandler([CommonFilters.reply, RegexpFilter(self.plain_pattern)], self.on_match), priority=70)

    def setup_schedules(self, adapter):
        pass

    def on_match(self, update):
        message = update.effective_message

        # No message
        if message is None:
            return

        text = message.text

        # Quit early if there's no text
        if len(text) == 0:
            return

        # Filter messages that are not replies
        if not message.reply_to_message:
            return

        # Filter replies to messages without text
        if len(message.reply_to_message.text) == 0:
            return

        # Check if we are getting s//
        match = self.pattern.match(text)
        if not match:
            return

        user_pattern = match.group('pattern')
        user_replacement = match.group('replacement')

        # Try compiling user pattern
        try:
            pattern = re.compile(user_pattern, flags=re.IGNORECASE)
            if not pattern:
                return

            response_text = pattern.sub("<b>{}</b>".format(user_replacement), message.reply_to_message.text)

            self.adapter.bot.sendMessage(chat_id=message.chat_id,
                                         text="<b>Did you mean</b>❔\n{}".format(response_text),
                                         parse_mode='HTML')
        except Exception as ex:
            log.info("Exception when compiling user pattern: {}".format(ex))
