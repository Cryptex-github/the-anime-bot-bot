from discord.ext import commands

from utils.subclasses import GlobalCooldown, AnimeContext


class Cooldown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_check(self.global_cooldown, call_once=True)
        self.normal_cooldown = commands.CooldownMapping.from_cooldown(5, 1, commands.BucketType.user)

    async def global_cooldown(self, ctx: AnimeContext):
        bucket = self.normal_cooldown.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if ctx.author.id == 590323594744168494:
            return True
        elif retry_after:
            raise GlobalCooldown(bucket, retry_after)
        else:
            return True


def setup(bot):
    bot.add_cog(Cooldown(bot))
