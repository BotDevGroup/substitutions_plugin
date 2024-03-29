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
            'pattern': r'^s/(?P<pattern>.+?)(?<!\\)/(?P<replacement>.*?)/(?P<flags>[giI]*)$'
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
        user_flags = match.group('flags')

        # Try compiling user pattern
        try:
            flags = re.IGNORECASE if 'i' in user_flags or 'I' in user_flags else 0

            pattern = re.compile(user_pattern, flags)
            if not pattern:
                return

            count = 0 if 'g' in user_flags else 1
            response_text = pattern.sub(user_replacement, message.reply_to_message.text, count=count)

            self.adapter.bot.sendMessage(chat_id=message.chat_id,
                                         reply_to_message_id=message.reply_to_message.message_id,
                                         text=response_text,
                                         disable_web_page_preview=True)
        except Exception as ex:
            log.info("Exception when compiling user pattern: {}".format(ex))
