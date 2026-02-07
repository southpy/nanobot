"""Channel manager for coordinating chat channels."""

import asyncio
from typing import Any

from loguru import logger

from nanobot.bus.events import OutboundMessage
from nanobot.bus.queue import MessageBus
from nanobot.channels.base import BaseChannel
from nanobot.config.schema import Config


class ChannelManager:
    """
    Manages chat channels and coordinates message routing.

    Responsibilities:
    - Initialize enabled channels (Telegram, WhatsApp, etc.)
    - Start/stop channels
    - Route outbound messages
    """

    def __init__(self, config: Config, bus: MessageBus):
        self.config = config
        self.bus = bus
        self.channels: dict[str, BaseChannel] = {}
        self._dispatch_task: asyncio.Task | None = None

        self._init_channels()

    def _init_channels(self, name: str | None = None) -> None:
        """Initialize channels based on config."""

        def init_tg():
            if self.config.channels.telegram.enabled and "telegram" not in self.channels:
                try:
                    from nanobot.channels.telegram import TelegramChannel

                    self.channels["telegram"] = TelegramChannel(
                        self.config.channels.telegram,
                        self.bus,
                        groq_api_key=self.config.providers.groq.api_key,
                    )
                    logger.info("Telegram channel enabled")
                except ImportError as e:
                    logger.warning(f"Telegram channel not available: {e}")

        def init_wa():
            if self.config.channels.whatsapp.enabled and "whatsapp" not in self.channels:
                try:
                    from nanobot.channels.whatsapp import WhatsAppChannel

                    self.channels["whatsapp"] = WhatsAppChannel(
                        self.config.channels.whatsapp, self.bus
                    )
                    logger.info("WhatsApp channel enabled")
                except ImportError as e:
                    logger.warning(f"WhatsApp channel not available: {e}")

        def init_dc():
            if self.config.channels.discord.enabled and "discord" not in self.channels:
                try:
                    from nanobot.channels.discord import DiscordChannel

                    self.channels["discord"] = DiscordChannel(
                        self.config.channels.discord, self.bus
                    )
                    logger.info("Discord channel enabled")
                except ImportError as e:
                    logger.warning(f"Discord channel not available: {e}")

        def init_fs():
            if self.config.channels.feishu.enabled and "feishu" not in self.channels:
                try:
                    from nanobot.channels.feishu import FeishuChannel

                    self.channels["feishu"] = FeishuChannel(self.config.channels.feishu, self.bus)
                    logger.info("Feishu channel enabled")
                except ImportError as e:
                    logger.warning(f"Feishu channel not available: {e}")

        initializers = {
            "telegram": init_tg,
            "whatsapp": init_wa,
            "discord": init_dc,
            "feishu": init_fs,
        }

        if name:
            if name in initializers:
                initializers[name]()
        else:
            for init_fn in initializers.values():
                init_fn()

    async def start_all(self) -> None:
        """Start WhatsApp channel and the outbound dispatcher."""
        if not self.channels:
            logger.warning("No channels enabled")
            return

        # Start outbound dispatcher
        self._dispatch_task = asyncio.create_task(self._dispatch_outbound())

        # Start WhatsApp channel
        tasks = []
        for name, channel in self.channels.items():
            logger.info(f"Starting {name} channel...")
            tasks.append(asyncio.create_task(channel.start()))

        # Wait for all to complete (they should run forever)
        await asyncio.gather(*tasks, return_exceptions=True)

    async def stop_all(self) -> None:
        """Stop all channels and the dispatcher."""
        logger.info("Stopping all channels...")

        # Stop dispatcher
        if self._dispatch_task:
            self._dispatch_task.cancel()
            try:
                await self._dispatch_task
            except asyncio.CancelledError:
                pass

        # Stop all channels
        for name, channel in self.channels.items():
            try:
                await channel.stop()
                logger.info(f"Stopped {name} channel")
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")

    async def _dispatch_outbound(self) -> None:
        """Dispatch outbound messages to the appropriate channel."""
        logger.info("Outbound dispatcher started")

        while True:
            try:
                msg = await asyncio.wait_for(self.bus.consume_outbound(), timeout=1.0)

                channel = self.channels.get(msg.channel)
                if channel:
                    try:
                        await channel.send(msg)
                    except Exception as e:
                        logger.error(f"Error sending to {msg.channel}: {e}")
                else:
                    logger.warning(f"Unknown channel: {msg.channel}")

            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break

    def get_channel(self, name: str) -> BaseChannel | None:
        """Get a channel by name."""
        return self.channels.get(name)

    def get_status(self) -> dict[str, Any]:
        """Get status of all channels."""
        return {
            name: {"enabled": True, "running": channel.is_running}
            for name, channel in self.channels.items()
        }

    async def update_config(self, config: Config) -> None:
        self.config = config

        new_channels_config = {
            "telegram": config.channels.telegram,
            "whatsapp": config.channels.whatsapp,
            "discord": config.channels.discord,
            "feishu": config.channels.feishu,
        }

        for name, channel_cfg in new_channels_config.items():
            existing_channel = self.channels.get(name)

            if channel_cfg.enabled and not existing_channel:
                self._init_channels(name)
                new_channel = self.channels.get(name)
                if new_channel:
                    asyncio.create_task(new_channel.start())
            elif not channel_cfg.enabled and existing_channel:
                await existing_channel.stop()
                del self.channels[name]
            elif channel_cfg.enabled and existing_channel:
                if hasattr(existing_channel, "update_config"):
                    update_fn = getattr(existing_channel, "update_config")
                    if asyncio.iscoroutinefunction(update_fn):
                        await update_fn(channel_cfg)
                    else:
                        update_fn(channel_cfg)

        logger.info("Channel manager configuration updated via hot reload")

    @property
    def enabled_channels(self) -> list[str]:
        """Get list of enabled channel names."""
        return list(self.channels.keys())
