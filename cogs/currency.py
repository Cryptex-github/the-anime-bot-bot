from discord.ext import commands


# class functions(commands.Cog):
#   async def buy_this(self, user,item_name,amount):
#     function = self.bot.get_cog("functions")
#     item_name = item_name.lower()
#     name_ = None
#     for item in self.mainshop:
#         name = item["name"].lower()
#         if name == item_name:
#             name_ = name
#             price = item["price"]
#             break

#     if name_ == None:
#         return [False,1]

#     cost = price*amount

#     users = await function.get_bank_data()

#     bal = await function.update_bank(user)

#     if bal[0]<cost:
#         return [False,2]


#     try:
#         index = 0
#         t = None
#         for thing in users[str(user.id)]["bag"]:
#             n = thing["item"]
#             if n == item_name:
#                 old_amt = thing["amount"]
#                 new_amt = old_amt + amount
#                 users[str(user.id)]["bag"][index]["amount"] = new_amt
#                 t = 1
#                 break
#             index+=1 
#         if t == None:
#             obj = {"item":item_name , "amount" : amount}
#             users[str(user.id)]["bag"].append(obj)
#     except:
#         obj = {"item":item_name , "amount" : amount}
#         users[str(user.id)]["bag"] = [obj]        

#     with open("bank.json","w") as f:
#         json.dump(users,f)

#     await function.update_bank(user,cost*-1,"wallets")

#     return [True,"Worked"]
#   async def sell_this(self, user,item_name,amount,price = None):
#     function = self.bot.get_cog("functions")
#     item_name = item_name.lower()
#     name_ = None
#     for item in self.mainshop:
#         name = item["name"].lower()
#         if name == item_name:
#             name_ = name
#             if price==None:
#                 price = 0.9* item["price"]
#             break

#     if name_ == None:
#         return [False,1]

#     cost = price*amount

#     users = await function.get_bank_data()

#     bal = await function.update_bank(user)


#     try:
#         index = 0
#         t = None
#         for thing in users[str(user.id)]["bag"]:
#             n = thing["item"]
#             if n == item_name:
#                 old_amt = thing["amount"]
#                 new_amt = old_amt - amount
#                 if new_amt < 0:
#                     return [False,2]
#                 users[str(user.id)]["bag"][index]["amount"] = new_amt
#                 t = 1
#                 break
#             index+=1 
#         if t == None:
#             return [False,3]
#     except:
#         return [False,3]    

#     with open("bank.json","w") as f:
#         json.dump(users,f)

#     await function.update_bank(user,cost,"wallets")

#     return [True,"Worked"]

#   async def update_bank(self, user, change=0, mode="wallets"):
#     function = self.bot.get_cog("functions")
#     users = await function.get_bank_data()
#     users[str(user.id)][mode] += change
#     with open("bank.json", "w") as f:
#       json.dump(users, f)
#     bal = [users[str(user.id)]["wallets"],users[str(user.id)]["banks"]]
#     return bal
#   async def get_bank_data():
#     with open("bank.json", "r") as f:
#         users = json.load(f)
#         return users


# async def open_account(self, user):
#     function = self.bot.get_cog("functions")
#     users = await function.get_bank_data()
#     if str(user.id) in users:
#       return False
#     else:
#         users[str(user.id)] = {}
#         users[str(user.id)]["wallets"] = 0
#         users[str(user.id)]["banks"] = 0
#         with open("bank.json", "w") as f:
#           json.dump(users, f)
#         return True


class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    #   self.anime_characters = ["inuyasha", "kageyama", "naruto", "luffy", "erwin", "yuno", "asta", "luck", "nami", "light yagami"]
    #   self.mainshop = [
    # {"name": "anime_pillow", "price": 1000, "description": " is a good pillow for you to put on your back so your back won't hurt when you watch anime for hours."},
    # {"name": "anime_body_pillow", "price": 5000, "description": " is a good big pillow that you can lay on sleep on or sit on it is big and good for watching anime for 24 hours tho"},
    # {"name": "plush",  "price": 500, "description": " is a small little plush that is cute."},
    # {"name": "laptop", "price": 10000, "description": " is needed for weebs to watching anime "}
    # ]
    # @commands.command()
    # async def sell(self, ctx,item,amount = 1):
    #   function = self.bot.get_cog("functions")
    #   await ctx.trigger_typing()
    #   await function.open_account(ctx.author)

    #   res = await function.sell_this(ctx.author,item,amount)

    #   if not res[0]:
    #     if res[1]==1:
    #       await ctx.reply("That Object isn't there!")
    #       return
    #     if res[1]==2:
    #       await ctx.reply(f"You don't have {amount} {item} in your bag.")
    #       return
    #     if res[1]==3:
    #       await ctx.reply(f"You don't have {item} in your bag.")
    #       return

    #   await ctx.reply(f"You just sold {amount} {item}.")
    # @commands.command()
    # async def bag(self, ctx):
    #   function = self.bot.get_cog("functions")
    #   await ctx.trigger_typing()
    #   await open_account(ctx.author)
    #   user = ctx.author
    #   users = await function.get_bank_data()

    #   try:
    #       bag = users[str(user.id)]["bag"]
    #   except:
    #         bag = []

    #   em = discord.Embed(title = "Bag")
    #   for item in bag:
    #     name = item["item"]
    #     amount = item["amount"]
    #     em.add_field(name = name, value = amount)
    #   await ctx.reply(embed = em)
    # @commands.command()
    # async def buy(self, ctx, item, amount=1):
    #   function = self.bot.get_cog("functions")
    #   await ctx.trigger_typing()
    #   await open_account(ctx.author)

    #   res = await function.buy_this(ctx.author,item,amount)
    #   if not res[0]:
    #     if res[1]==1:
    #       await ctx.reply("That Object isn't there!")
    #       return
    #     if res[1]==2:
    #       await ctx.reply(f"You don't have enough money in your wallet to buy {amount} {item}")
    #       return
    #   await ctx.reply(f"You just bought {amount} {item}")
    # @commands.command()
    # async def shop(self, ctx):
    #   function = self.bot.get_cog("functions")
    #   await ctx.trigger_typing()
    #   embed = discord.Embed(color=0x2ecc71)
    #   embed.set_author(name="shop")
    #   for item in self.mainshop:
    #     name = item["name"]
    #     price = item["price"]
    #     description = item["description"]
    #     embed.add_field(name= name, value= f" {price} \n {description}", inline=False)
    #   await ctx.reply(embed=embed)
    # @commands.command(aliases=["with"])
    # async def withdraw(self, ctx, amount=None):
    #   function = self.bot.get_cog("functions")
    #   await ctx.trigger_typing()
    #   await open_account(ctx.author)
    #   if amount == None:
    #     await ctx.reply("Please specific a amount to withdraw")
    #     return
    #   bal = await function.update_bank(ctx.author)
    #   if amount == "all":
    #     amount = bal[1]
    #   amount = int(amount)
    #   if amount > bal[1]:
    #     await ctx.reply("You don't have that many 🍓 ")
    #     return
    #   if amount < 0:
    #     await ctx.reply("It must be positive")
    #     return
    #   await function.update_bank(ctx.author, amount)
    #   await function.update_bank(ctx.author, -1*amount, "banks")
    #   await ctx.reply(f"You withdrawn {amount} coins")

    # @commands.command(brief=" steal someone's wallet")
    # @commands.Cooldown(1, 300, commands.BucketType.user)
    # async def steal(self, ctx, member : discord.Member):
    #   function = self.bot.get_cog("functions")
    #   await ctx.trigger_typing()
    #   await open_account(ctx.author)
    #   await open_account(member)
    #   author_bal = await function.update_bank(ctx.author)
    #   bal = await function.update_bank(member)
    #   if bal[0] < 100:
    #     await ctx.reply(" is not worth it man ")
    #     return
    #   if author_bal[0] < 100:
    #     await ctx.reply(" You need at least 100 berries in wallets in order to steal someone else ")
    #     return
    #   earnings = random.randrange(0, bal[0])
    #   if earnings == 0:
    #     ctx.reply(" You get caught by police and you lose all your berries in wallets ")
    #     await function.update_bank(ctx.author, -1*author_bal[0])
    #     return
    #   await ctx.reply(f" good job man you stole {earnings} berries")
    #   await function.update_bank(ctx.author, earnings)
    #   await function.update_bank(member, -1*earnings)
    # @commands.command()
    # @commands.Cooldown(1, 60, commands.BucketType.user)
    # async def slot(self, ctx, amount=None):
    #   function = self.bot.get_cog("functions")
    #   await ctx.trigger_typing()
    #   await open_account(ctx.author)
    #   if amount == None:
    #     await ctx.reply("Please specific a amount to slot")
    #     return
    #   bal = await function.update_bank(ctx.author)
    #   amount = int(amount)
    #   if amount > bal[0]:
    #     await ctx.reply("You don't have that many 🍓 ")
    #     return
    #   if amount < 0:
    #     await ctx.reply("It must be positive")
    #     return
    #   final = []
    #   for i in range(3):
    #     a = random.choice(["X","O","Q"])
    #     final.append(a)
    #   await ctx.reply(str(final))
    #   if final[0] == final[1] or final[1] == final[2] or final[0] == final[1] == final[2]:
    #     await function.update_bank(ctx.author, 1.5*amount)
    #     await ctx.reply(f"you won {1.5*amount} 🍓 ")
    #   else:
    #     await function.update_bank(ctx.author, -1*amount)
    #     await ctx.reply(f"you lose {-1*amount} 🍓 ")

    # @commands.command()
    # async def send(self, ctx, member : discord.Member, amount=None):
    #   function = self.bot.get_cog("functions")
    #   await ctx.trigger_typing()
    #   await open_account(ctx.author)
    #   await open_account(member)
    #   if amount == None:
    #     await ctx.reply("Please specific a amount to send")
    #     return
    #   bal = await function.update_bank(ctx.author)
    #   amount = int(amount)
    #   if amount > bal[0]:
    #     await ctx.reply("You don't have that many 🍓 ")
    #     return
    #   if amount < 0:
    #     await ctx.reply("It must be positive")
    #     return
    #   await function.update_bank(member, amount)
    #   await function.update_bank(ctx.author, -1*amount)
    #   await ctx.reply(f"You send {amount} coins")
    # @commands.command(aliases=["dep"])
    # async def deposit(self, ctx, amount=None):
    #   function = self.bot.get_cog("functions")
    #   await ctx.trigger_typing()
    #   await open_account(ctx.author)
    #   if amount == None:
    #     await ctx.reply("Please specific a amount to deposit")
    #     return
    #   bal = await function.update_bank(ctx.author)
    #   if amount == "all":
    #     amount = bal[0]
    #   amount = int(amount)
    #   if amount > bal[0]:
    #     await ctx.reply("You don't have that many 🍓 ")
    #     return
    #   if amount < 0:
    #     await ctx.reply("It must be positive")
    #   await function.update_bank(ctx.author, amount, "banks")
    #   await function.update_bank(ctx.author, -1*amount)
    #   await ctx.reply(f"You deposit {amount} coins")
    # @commands.command(aliases=["bal"])
    # async def balance(self, ctx):
    #     function = self.bot.get_cog("functions")
    #     await ctx.trigger_typing()
    #     await function.open_account(ctx.author)
    #     user = ctx.author
    #     users = await function.get_bank_data()
    #     wallet = users[str(user.id)]["wallets"]
    #     bank = users[str(user.id)]["banks"]
    #     embed = discord.Embed(title=f"{ctx.author.name}'s account balance", color=0x2ecc71)
    #     embed.add_field(name="wallet Balance ", value=f"{wallet} 🍓 ")
    #     embed.add_field(name="bank balance ", value=f"{bank} 🍓 ")
    #     await ctx.reply(embed=embed)
    # anime_characters = ["inuyasha", "kageyama", "naruto", "luffy", "erwin", "yuno", "asta", "luck", "nami", "light yagami"]
    # @commands.command()
    # async def beg(self, ctx):
    #   function = self.bot.get_cog("functions")
    #   await ctx.trigger_typing()
    #   await open_account(ctx.author)
    #   user = ctx.author
    #   users = await function.get_bank_data()
    #   earnings = random.randrange(300)
    #   embed = discord.Embed(color=0x2ecc71, description=f" {random.choice(self.anime_characters)} gave you {earnings} 🍓  ")
    #   embed.set_author(name="Beg ")
    #   await ctx.reply(embed=embed)
    #   users[str(user.id)]["wallets"] += earnings
    #   with open("bank.json", "w") as f:
    #     json.dump(users, f)


def setup(bot):
    bot.add_cog(currency(bot))
