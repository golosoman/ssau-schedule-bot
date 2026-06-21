from aiogram import Bot
from dependency_injector import containers, providers

from app.app_layer.interfaces.notifications.notifier.interface import INotifier
from app.app_layer.interfaces.telegram.chat_checker.interface import ITelegramChatChecker
from app.app_layer.interfaces.telegram.renderer.interface import ITelegramMessageRenderer
from app.app_layer.interfaces.telegram.sender.interface import ITelegramMessageSender
from app.infra.clients.telegram.bot import AiogramTelegramBot, create_bot
from app.infra.clients.telegram.chat_checker import TelegramChatChecker
from app.infra.clients.telegram.interface import ITelegramBot
from app.infra.clients.telegram.message_renderer import AiogramTelegramMessageRenderer
from app.infra.clients.telegram.message_sender import TelegramMessageSender
from app.infra.clients.telegram.notifier import TelegramNotifier
from app.infra.clients.telegram.settings import TelegramClientSettings
from app.infra.retry import RetryPolicy
from app.settings.config import settings


def _telegram_bot_token() -> str:
    return settings.telegram.bot_token.get_secret_value()


class TelegramContainer(containers.DeclarativeContainer):
    metrics = providers.DependenciesContainer()

    bot: providers.Provider[Bot] = providers.Resource(
        create_bot,
        settings=providers.Singleton(
            TelegramClientSettings,
            bot_token=providers.Callable(_telegram_bot_token),
            proxy_url=settings.telegram.proxy_url,
        ),
    )
    retry_policy: providers.Provider[RetryPolicy] = providers.Singleton(
        RetryPolicy,
        max_attempts=settings.telegram.retry.max_attempts,
        base_delay=settings.telegram.retry.base_seconds,
        max_delay=settings.telegram.retry.max_seconds,
        jitter=settings.telegram.retry.jitter_seconds,
    )
    renderer: providers.Provider[ITelegramMessageRenderer] = providers.Singleton(
        AiogramTelegramMessageRenderer,
    )
    bot_client: providers.Provider[ITelegramBot] = providers.Singleton(
        AiogramTelegramBot,
        bot=bot,
    )
    sender: providers.Provider[ITelegramMessageSender] = providers.Singleton(
        TelegramMessageSender,
        bot=bot_client,
        retry_policy=retry_policy,
    )
    chat_checker: providers.Provider[ITelegramChatChecker] = providers.Singleton(
        TelegramChatChecker,
        bot=bot_client,
        retry_policy=retry_policy,
    )
    notifier: providers.Provider[INotifier] = providers.Factory(
        TelegramNotifier,
        renderer=renderer,
        sender=sender,
        metrics=metrics.metrics_service,
    )
