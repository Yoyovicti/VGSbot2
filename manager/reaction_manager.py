from typing import List

import interactions


class ReactionManager:
    def __init__(self, message: interactions.Message, emojis: List[str]):
        self.message = message
        self.emojis = emojis

    async def run(self) -> str:
        for emoji in self.emojis:
            await self.message.add_reaction(emoji)

        message_reaction = await self.message.client.wait_for("MessageReactionAdd", self.detect_reaction,
                                                              timeout=86400)
        # debug
        print(f"===== ReactionManager Debug =====\n"
              f"{message_reaction.message}\n"
              f"{message_reaction.author}\n"
              f"{message_reaction.emoji}\n"
              f"{message_reaction.reaction}")
        return message_reaction.emoji.name

    async def detect_reaction(self, event: interactions.api.events.MessageReactionAdd) -> bool:
        """
        Checks if a reaction has been added by a user on the message.
        """
        if event.message.id == self.message.id:
            if not event.author.bot:
                emoji = event.emoji.name
                if event.emoji.id is not None:
                    emoji = f"<:{emoji}:{event.emoji.id}>"
                return emoji in self.emojis
        return False
