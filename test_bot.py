"""Offline smoke tests for bot configuration and command registration.

These tests deliberately do not log in to Discord or require a bot token.
"""
import os
import unittest
from unittest.mock import patch

import bot as bot_module


class BotConfigurationTests(unittest.TestCase):
    def test_missing_token_has_actionable_error(self):
        with patch.dict(os.environ, {"DISCORD_TOKEN": "  "}):
            with self.assertRaisesRegex(RuntimeError, "DISCORD_TOKEN is not configured"):
                bot_module.get_discord_token()

    def test_configured_token_is_read_from_environment(self):
        with patch.dict(os.environ, {"DISCORD_TOKEN": "example-test-token"}):
            self.assertEqual(bot_module.get_discord_token(), "example-test-token")

    def test_expected_commands_are_registered(self):
        expected = {
            "help", "ping", "meme", "joke", "8ball", "roll",
            "flip", "avatar", "userinfo", "saymyname", "time", "choose",
        }
        registered = {command.name for command in bot_module.bot.commands}
        self.assertTrue(expected.issubset(registered), expected - registered)

    def test_only_message_content_is_required_as_privileged_intent_by_default(self):
        intents = bot_module.bot.intents
        self.assertTrue(intents.message_content)
        self.assertFalse(intents.members)
        self.assertFalse(intents.presences)

    def test_subreddit_argument_validation(self):
        self.assertIsNone(bot_module.SUBREDDIT_PATTERN.fullmatch("r/memes"))
        self.assertIsNotNone(bot_module.SUBREDDIT_PATTERN.fullmatch("ProgrammerHumor"))

    def test_meme_image_urls_must_be_https_direct_images(self):
        self.assertTrue(bot_module._is_direct_image_url("https://i.redd.it/example.jpg"))
        self.assertTrue(bot_module._is_direct_image_url("https://cdn.example.org/meme.webp"))
        self.assertFalse(bot_module._is_direct_image_url("http://i.redd.it/example.jpg"))
        self.assertFalse(bot_module._is_direct_image_url("https://reddit.com/r/memes"))


if __name__ == "__main__":
    unittest.main()
