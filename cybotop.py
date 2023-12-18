
import discord
import matplotlib
from matplotlib import pyplot
from matplotlib import dates
import random
from discord.ui import View
from discord import ui
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
from typing import Optional
import os
from datetime import timedelta
from datetime import datetime
from datetime import date
from discord.ext.commands import Bot
import psycopg2
import requests
import asyncio
from discord.ext.commands import MemberConverter
from datetime import datetime, timedelta
from discord.ext import tasks
from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)
conn = psycopg2.connect("postgres://cybot:TdF93F0D7Hg26Wr9icHwjJpOnah9lpe2@dpg-cm0167eg1b2c73cl5ke0-a/bot_mbx0")

cur = conn.cursor()
cur.execute('create table if not exists scoringyess ( UId text primary key, Score integer )')
conn.commit()
cur.execute('create table if not exists reactions ( messageId text primary key)')
conn.commit()
cur.execute('create table if not exists dailyProblems ( ContestID integer, Index text )')
conn.commit()
cur.execute('create table if not exists disc_cf_id (DiscID text primary key, Cf_ID text)')
conn.commit()
cur.execute('create table if not exists PROBLEMS (ContestID integer,Index text,Rating integer, Name text)')
conn.commit()
cur.execute('create table if not exists SoloLeaderboard (DiscordID text primary key, score integer)')
conn.commit()
cur.execute('create table if not exists DuelLeaderboard (DiscordID text primary key, score integer)')
conn.commit()
cur.execute(
    'create table if not exists Sololevelling ( userdisc text primary key, usercf text, contestid integer, '
    'index text, startTime text)')
conn.commit()
cur.execute(
    'create table if not exists duelchallenge(user1 text primary key, user2 text, ContestID integer, index text, '
    'startTime text)')
conn.commit()
intents = discord.Intents.default()
intents.message_content = True
tag_list = [
    'implementation',
    'math',
    'greedy',
    'dp',
    'data structures',
    'brute force',
    'constructive algorithms',
    'graphs',
    'sortings',
    'binary search',
    'dfs and similar',
    'trees',
    'strings',
    'number theory',
    'combinatorics',
    'geometry',
    'bitmasks',
    'two pointers',
    'dsu',
    'shortest paths',
    'probabilities',
    'divide and conquer',
    'hashing',
    'games',
    'flows',
    'interactive',
    'matrices',
    'string suffix structures',
    'fft',
    'graph matchings',
    'ternary search',
    'expression parsing',
    'meet-in-the-middle',
    '2-sat',
    'chinese remainder theorem',
    'schedules']
duelrating = None


class ButtonYesNo(View):
    user1 = None
    inter = None

    def __init__(self, Interaction: discord.Interaction, timeout: float, user: discord.Member) -> None:
        super().__init__(timeout=timeout)

        self.user1 = user
        self.inter = Interaction
        print(user)
        self.user = user

    @ui.button(emoji="✅", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):

        print(f"{interaction.user} {self.user1} ")
        global duelrating
        global taglisduel
        if interaction.user == self.user1:
            user1 = self.inter.user.id
            user2 = self.user1.id
            cur.execute('select Cf_id from disc_cf_id where DiscID =%s or DiscID = %s', (str(user1), str(user2),))
            conn.commit()
            rows = cur.fetchall()
            handle1 = rows[0][0]
            handle2 = rows[1][0]
            user1doneporblems = await get_user_problems(handle1)
            user2doneproblems = await get_user_problems(handle2)
            alldoneproblems = user1doneporblems + user2doneproblems
            alldoneproblems = list(alldoneproblems)
            if duelrating is not None and (duelrating < 800 or duelrating > 3500 or duelrating % 100 != 0):
                await self.inter.edit_original_response("Rating dhang se daal")
            else:
                unsolvedprobs = await get_user_unsolved_problems(alldoneproblems, duelrating, None)
                if not unsolvedprobs:
                    await self.inter.edit_original_response(f"Nahi hai bhai question Bank me", view=None)
                    return
                unsolgiven = random.choice(unsolvedprobs)
                linktobesold = "https://codeforces.com/contest/" + str(unsolgiven[0]) + "/problem/" + str(
                    unsolgiven[1])
                now = datetime.now()
                now1 = str(now)
                now1 = now1.split(".")
                cur.execute('Insert into duelchallenge values(%s,%s,%s,%s,%s)',
                            (str(self.inter.user.id), str(interaction.user.id), unsolgiven[0], unsolgiven[1], now1[0],))
                conn.commit()
                desc = f"your time has come go solve [this]({linktobesold})"
                ti = "Here is your problem"
                embed =await send_embed(ti, desc)
                await self.inter.edit_original_response(embed=embed, view=None)

        else:
            await interaction.response.send_message('Tere lie nahi tha bhai', ephemeral=True)
        pass

    @ui.button(emoji="⛔", style=discord.ButtonStyle.red)
    async def no(self, interaction, button):
        if interaction.user == self.user1:
            await self.inter.edit_original_response(
                embed=await send_embed("Battle Declined", "Its not the first time you are rejected"), view=None)
        else:
            await interaction.response.send_message('Tere lie nahi tha bhai', ephemeral=True)
        pass


class ButtonYesNoduel_end(View):
    user1 = None
    inter = None

    def __init__(self, Interaction: discord.Interaction, timeout: float, user: discord.Member) -> None:
        super().__init__(timeout=timeout)

        self.user1 = user
        self.inter = Interaction
        self.user = user

    @ui.button(emoji="✅", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):

        print(f"{interaction.user} {self.user1} ")
        global duelrating
        global taglisduel
        if str(interaction.user.id) == str(self.user1):
            ti = "Result"
            desc = "The duel has ended in a Draw."
            cur.execute("delete from duelchallenge where user1=%s or user2=%s", (str(interaction.user.id),
                                                                                 str(interaction.user.id),))
            conn.commit()
            await self.inter.edit_original_response(embed=await send_embed(ti, desc), view=None)
        else:
            await interaction.response.send_message('Tere lie nahi tha bhai', ephemeral=True)

    @ui.button(emoji="⛔", style=discord.ButtonStyle.red)
    async def no(self, interaction, button):
        if str(interaction.user.id) == str(self.user1):
            await self.inter.edit_original_response(
                embed=await send_embed("Draw Declined", "Looks like your opponent has some ideas up his sleeve. Buckle up"),
                view=None)
        else:
            await interaction.response.send_message('Tere lie nahi tha bhai', ephemeral=True)


async def get_user_problems(handle):
    user_problems = []
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    response = await requests.get(url)
    data = response.json()
    result = data['result']

    for x in result:
        if x['verdict'] is None:
            continue
        elif x['verdict'] == 'OK':
            user_problems.append([x['problem']['contestId'], x['problem']['index']])

    return user_problems


async def get_user_unsolved_problems(user_problems, rating, tags):
    unsolved_user_problems = []
    if rating is None:
        cur.execute('SELECT ContestID, Index, Rating, Tags from PROBLEMS')
    else:
        cur.execute("SELECT * from PROBLEMS  where Rating = %s", (str(rating),))
    conn.commit()
    rows = cur.fetchall()

    for row in rows:
        bol = 1
        if tags:

            for tag in tags:
                i = 0
                while i < 35:
                    if tag_list[i] == tag:
                        break
                    i += 1
                if row[4][i] == 0:
                    bol = 0
                    break
            if bol == 0:
                continue
        for x in user_problems:
            if x[0] == row[0] and x[1] == row[1]:
                bol = 0
                break

        if bol == 1:
            unsolved_user_problems.append([row[0], row[1], row[3]])

    return unsolved_user_problems


async def unixTimeToHumanReadableVaibhav(seconds):
    # Save the time in Human
    # readable format
    ans = ""

    # Number of days in month
    # in normal year
    daysOfMonth = [31, 28, 31, 30, 31, 30,
                   31, 31, 30, 31, 30, 31]

    (currYear, daysTillNow, extraTime,
     extraDays, index, date, month, hours,
     minutes, secondss, flag) = (0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0)

    # Calculate total days unix time T
    daysTillNow = seconds // (24 * 60 * 60)
    extraTime = seconds % (24 * 60 * 60)
    currYear = 1970

    # Calculating current year
    while (daysTillNow >= 365):
        if (currYear % 400 == 0 or
                (currYear % 4 == 0 and
                 currYear % 100 != 0)):
            if daysTillNow < 366:
                break
            daysTillNow -= 366

        else:
            daysTillNow -= 365

        currYear += 1

    # Updating extradays because it
    # will give days till previous day,
    # and we have included current day
    extraDays = daysTillNow + 1

    if (currYear % 400 == 0 or
            (currYear % 4 == 0 and
             currYear % 100 != 0)):
        flag = 1

    # Calculating MONTH and DATE
    month = 0
    index = 0

    if (flag == 1):
        while (True):

            if (index == 1):
                if (extraDays - 29 < 0):
                    break

                month += 1
                extraDays -= 29

            else:
                if (extraDays - daysOfMonth[index] < 0):
                    break

                month += 1
                extraDays -= daysOfMonth[index]

            index += 1

    else:
        while (True):
            if (extraDays - daysOfMonth[index] < 0):
                break

            month += 1
            extraDays -= daysOfMonth[index]
            index += 1

    # Current Month
    if (extraDays > 0):
        month += 1
        date = extraDays

    else:
        if (month == 2 and flag == 1):
            date = 29
        else:
            date = daysOfMonth[month - 1]

    # Calculating HH:MM:YYYY
    hours = extraTime // 3600
    minutes = (extraTime % 3600) // 60
    secondss = (extraTime % 3600) % 60

    ans += str(currYear)
    ans += "-"
    ans += str(month)
    ans += "-"
    ans += str(date)
    # ans += " "
    # # ans += str(hours)
    # # ans += ":"
    # # ans += str(minutes)
    # # ans += ":"
    # # ans += str(secondss)

    # Return the time
    return ans


async def send_embed(ti, desc):
    embed = discord.Embed(
        colour=discord.Colour.dark_teal(),
        description=desc,
        title=ti
    )
    return embed


bot = commands.Bot(command_prefix="/", intents=intents, )
bot_button_message_id = None


@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f"Slash commands synced and lenght is " + str(len(synced)) + "commnads")
    await reminder.start()
    await daily_problems.start()


async def unixToHumanandUtkarsh(seconds):
    ans = ""
    extraTime = seconds % (24 * 60 * 60)
    hours = extraTime // 3600
    minutes = (extraTime % 3600) // 60
    minutes += 30
    if minutes >= 60:
        hours += 1
        minutes = minutes - 60
    hours += 5
    if hours >= 24:
        hours = hours - 24

    if hours < 10:
        ans += '0'
    ans += str(hours)
    ans += ":"
    if minutes < 10:
        ans += '0'
    ans += str(minutes)

    return ans


async def unixTimeToHumanReadable(seconds):
    # Save the time in Human
    # readable format
    ans = []

    # Number of days in month
    # in normal year
    daysOfMonth = [31, 28, 31, 30, 31, 30,
                   31, 31, 30, 31, 30, 31]

    (currYear, daysTillNow, extraTime,
     extraDays, index, date, month, hours,
     minutes, secondss, flag) = (0, 0, 0, 0, 0,
                                 0, 0, 0, 0, 0, 0)

    # Calculate total days unix time T
    daysTillNow = seconds // (24 * 60 * 60)
    extraTime = seconds % (24 * 60 * 60)
    currYear = 1970

    # Calculating current year
    while daysTillNow >= 365:
        if (currYear % 400 == 0 or
                (currYear % 4 == 0 and
                 currYear % 100 != 0)):
            if daysTillNow < 366:
                break
            daysTillNow -= 366

        else:
            daysTillNow -= 365

        currYear += 1

    # Updating extradays because it
    # will give days till previous day,
    # and we have included current day
    extraDays = daysTillNow + 1

    if (currYear % 400 == 0 or
            (currYear % 4 == 0 and
             currYear % 100 != 0)):
        flag = 1

    # Calculating MONTH and DATE
    month = 0
    index = 0

    if flag == 1:
        while True:

            if index == 1:
                if extraDays - 29 < 0:
                    break

                month += 1
                extraDays -= 29

            else:
                if index >= 12 or extraDays - daysOfMonth[index] < 0:
                    break

                month += 1
                extraDays -= daysOfMonth[index]

            index += 1

    else:
        while True:
            if index >= 12 or extraDays - daysOfMonth[index] < 0:
                break

            month += 1
            extraDays -= daysOfMonth[index]
            index += 1

    # Current Month
    if extraDays > 0:
        month += 1
        date = extraDays

    else:
        if month == 2 and flag == 1:
            date = 29
        else:
            date = daysOfMonth[month - 1]

    # Calculating HH:MM:YYYY
    hours = extraTime // 3600
    minutes = (extraTime % 3600) // 60
    secondss = (extraTime % 3600) % 60

    mo1 = str(month)
    d1 = str(date)
    h1 = str(hours)
    m1 = str(minutes)
    s1 = str(secondss)

    if hours < 10:
        h1 = "0" + h1
    if minutes < 10:
        m1 = "0" + m1
    if secondss < 10:
        s1 = "0" + s1
    if month < 10:
        mo1 = "0" + mo1
    if date < 10:
        d1 = "0" + d1

    ans.append(currYear)
    ans.append(mo1)
    ans.append(d1)
    ans.append(h1)
    ans.append(m1)
    ans.append(s1)

    # Return the time
    return ans


@tasks.loop(seconds=3600)
async def reminder():
    url = "https://codeforces.com/api/contest.list?"
    channel = bot.get_channel(1056929299501953104)
    response = await requests.get(url)
    data = response.json()
    result = data['result']
    ts = result[0]['startTimeSeconds']
    contest = result[0]['name']
    for r in result:
        if r['startTimeSeconds'] < ts and r['phase'] == "BEFORE":
            ts = r['startTimeSeconds']
            contest = r['name']
        if r['phase'] == "FINISHED":
            break
    t1 = await unixTimeToHumanReadable(ts)
    now = datetime.now()
    now1 = str(now)
    now1 = now1.split(".")
    t2 = now1[0]
    datetime_str = str(t1[1]) + "/" + str(t1[2]) + "/" + str(t1[0]) + " " + str(t1[3]) + ":" + str(t1[4]) + ":" + str(
        t1[5])
    timechage = timedelta(hours=5, minutes=30)

    datetime_object = datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S')
    datetime_object += timechage
    print(datetime_object)
    datetime_object1 = datetime.strptime(t2, '%Y-%m-%d %H:%M:%S')
    time_remaining = datetime_object - datetime_object1
    t = time_remaining.total_seconds() / (60 * 60)
    if 2 > t > 0:
        desc = f"@everyone {contest} begins at {datetime_object}"
        title = 'Contest Reminder'
        await channel.send(desc)


@tasks.loop(hours=24)
async def daily_problems():
    channel = bot.get_channel(1056929299501953104)
    cur.execute("select * from dailyProblems")
    conn.commit()
    rows = cur.fetchall()
    solved = []
    for row in rows:
        solved.append([row[0], row[1]])
    rating = random.choice([800, 900, 1000])
    tags = []
    unsolved = await get_user_unsolved_problems(solved, rating, tags)
    unsolved1 = random.sample(unsolved, 2)
    link1 = "https://codeforces.com/contest/" + str(unsolved1[0][0]) + "/problem/" + str(unsolved1[0][1])
    link2 = "https://codeforces.com/contest/" + str(unsolved1[1][0]) + "/problem/" + str(unsolved1[1][1])
    cur.execute('Insert into dailyProblems values(%s,%s)', (unsolved1[0][0], str(unsolved1[0][1]),))
    cur.execute('Insert into dailyProblems values(%s,%s)', (unsolved1[1][0], str(unsolved1[1][1]),))
    conn.commit()
    emoji = "✅"
    mes1 = await channel.send(link1)
    await mes1.add_reaction(emoji)
    mes2 = await channel.send(link2)
    await mes2.add_reaction(emoji)


async def asking_compilation_error(Interaction, handlename, random_key):
    handlemention = Interaction.user
    print(handlename)

    linktorecentsub = "https://codeforces.com/api/user.status?handle=" + handlename + "&from=1&count=1"

    embed = discord.Embed(
        colour=discord.Colour.dark_teal(),
        description=f"{Interaction.user.mention} Submit a compilation error "
                    f"to this problem 👉 [{random_key}]({handlesetproblems[random_key]})",
        title='Identify Yourself'
    )
    embed.set_image(
        url="https://i0.wp.com/greglawlegal.com/wp-content/uploads/2016/07/Do-You-Need-To-Identify-Yourself-To-Law"
            "-Enforcement-Utah.png")
    return embed


handlesetproblems = {"System Administrator": "https://codeforces.com/problemset/problem/245/A",
                     "Four Segments": "https://codeforces.com/problemset/problem/1468/E",
                     "DZY Loves Hash": "https://codeforces.com/problemset/problem/447/A",
                     "Display Size": "https://codeforces.com/problemset/problem/747/A",
                     "Palindromic Supersequence": "https://codeforces.com/problemset/problem/932/A",
                     "Johny Likes Numbers": "https://codeforces.com/problemset/problem/678/A",
                     "Sleuth": "https://codeforces.com/problemset/problem/49/A",
                     "Glory Addicts": "https://codeforces.com/problemset/problem/1738/A",
                     "A pile of stones": "https://codeforces.com/problemset/problem/1159/A",
                     "Triangular numbers": "https://codeforces.com/problemset/problem/47/A",
                     "The Doors": "https://codeforces.com/problemset/problem/1143/A"}


@bot.command()
async def ping(ctx):
    desc = f'@everyone'
    ti = 'hello'
    await ctx.send(f"@everyone")


def changearg(arg):
    if arg != 'meet-in-the-middle' and arg != '2-sat':
        arg = arg.replace('-', ' ')
    print(arg)
    return arg


@bot.tree.command(name="upcoming_contests", description="Gives you upcoming contests from codeforces")
async def upcoming_contests(Interaction: discord.Interaction):
    await Interaction.response.defer()
    url = "https://codeforces.com/api/contest.list?"
    response = await requests.get(url)
    data = response.json()
    result = data['result']
    list = []
    for r in result:
        if r['phase'] == "BEFORE":
            ts = r['startTimeSeconds']
            t1 = await unixTimeToHumanReadable(ts)
            now = datetime.now()
            now1 = str(now)
            now1 = now1.split(".")
            t2 = now1[0]
            datetime_str = str(t1[1]) + "/" + str(t1[2]) + "/" + str(t1[0]) + " " + str(t1[3]) + ":" + str(
                t1[4]) + ":" + str(
                t1[5])
            timechage = timedelta(hours=5, minutes=30)

            datetime_object = datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S')
            datetime_object += timechage
            contest = r['name']
            d1 = datetime_object.strftime("%b/%d/%Y %H:%M")
            list.append([contest, d1])
        if r['phase'] == "FINISHED":
            break
    contests = ""
    list.reverse()
    x = 1
    for w in list:
        contests += f"{x}. {w[0]} on {w[1]}\n\n"
        x += 1
    desc = f"{contests}"
    ti = "Upcoming Contests- "
    embed = await send_embed(ti, desc)
    await Interaction.edit_original_response(embed=embed)


@bot.tree.command(name="solo_arise", description="Selects a problem for you to arise from codeforces")
@app_commands.describe(tags='Enter upto 5 tags seprated by commas and then a space')
@app_commands.describe(rating='Enter the rating of problem you want to solve ')
async def solo_arise(Interaction: discord.Interaction, rating: int = None, tags: str = None):
    await Interaction.response.defer()
    taglis = []
    if tags is not None:
        taglis = tags.split(', ')
    cur.execute('select userdisc from sololevelling where userdisc=%s', (str(Interaction.user.id),))
    conn.commit()
    roww = cur.fetchall()
    if roww:
        desc = 'You are already in solo Complete you ongoing solo by using solo_complete command'
        ti = 'Already in solo'
        embed = await send_embed(ti, desc)
        await Interaction.edit_original_response(embed=embed)
        return
    cur.execute('select Cf_ID from disc_cf_id where DiscID=%s', (str(Interaction.user.id),))
    conn.commit()
    row = cur.fetchall()
    if row is None:
        desc = 'You have not identified your handle to do so use !handle identify <cf_id>'
        ti = 'Identification Pending'
        embed = await send_embed(ti, desc)
        await Interaction.edit_original_response(embed=embed)
        return
    else:
        user_probs = await get_user_problems(row[0][0])
        if rating is not None and (rating < 800 or rating > 3500 or rating % 100 != 0):
            await Interaction.edit_original_response("Rating dhang se daal")
        else:
            unsolvedprobs = await get_user_unsolved_problems(user_probs, rating, taglis)
            if not unsolvedprobs:
                await Interaction.edit_original_response(f"Nahi hai bhai question Bank me")
                return
            unsolgiven = random.choice(unsolvedprobs)
            now = datetime.now()
            now1 = str(now)
            now1 = now1.split(".")
            linktobesold = "https://codeforces.com/contest/" + str(unsolgiven[0]) + "/problem/" + str(unsolgiven[1])
            cur.execute('insert into sololevelling values(%s,%s,%s,%s,%s)',
                        (str(Interaction.user.id), row[0][0], unsolgiven[0], unsolgiven[1], now1[0],))
            conn.commit()
            conn.commit()
            desc = f"your time has come go solve [this]({linktobesold})"
            ti = "Here is your problem"
            embed = await send_embed(ti, desc)
            await Interaction.edit_original_response(embed=embed)


@bot.tree.command(name="solo_end", description="Ends your ongoing solo")
async def solo_end(Interaction: discord.Interaction):
    await Interaction.response.defer()
    user = str(Interaction.user.id)
    cur.execute('select * from sololevelling where userdisc=%s', (user,))
    conn.commit()
    rows = cur.fetchall()
    if not rows:
        desc = 'You are not in solo'
        ti = 'Go level up!'
        embed = await send_embed(ti, desc)
        await Interaction.edit_original_response(embed=embed)
        return
    url = f"https://codeforces.com/api/user.status?handle={rows[0][1]}&from=1&count=30"
    response = await requests.get(url)
    data = response.json()
    result = data['result']
    booea = 0
    rating = 0
    for res in result:
        if res['problem']['contestId'] == rows[0][2] and res['problem']['index'] == rows[0][3]:
            if res['verdict'] == 'OK':
                rating = res['problem']['rating']
                unixt1 = res['creationTimeSeconds']
                booea = 1
                break
    if booea == 1:
        cur.execute("SELECT score from SoloLeaderboard where DiscordId = %s", (str(Interaction.user.id),))
        score = cur.fetchall()
        newscore = score[0][0] + ((int(rating) // 100) * (int(rating) // 100))
        cur.execute("UPDATE SoloLeaderboard set score = %s where DiscordId = %s", (newscore, str(Interaction.user.id),))
        conn.commit()
        t2 = rows[0][4]
        t1 = await unixTimeToHumanReadable(unixt1)
        datetime_str = str(t1[1]) + "/" + str(t1[2]) + "/" + str(t1[0]) + " " + str(t1[3]) + ":" + str(
            t1[4]) + ":" + str(t1[5])
        datetime_object = datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S')
        time_change = timedelta(hours=5, minutes=30)
        new_time = datetime_object + time_change
        datetime_object1 = datetime.strptime(t2, '%Y-%m-%d %H:%M:%S')
        duration = new_time - datetime_object1
        desc = f'''You have levelled up 
        time taken:- {duration}'''
        ti = 'Level Up!'
        embed = await send_embed(ti, desc)
        await Interaction.edit_original_response(embed=embed)
    else:
        cur.execute("SELECT score from SoloLeaderboard where DiscordId = %s", (str(Interaction.user.id),))
        score = cur.fetchall()
        newscore = score[0][0] - 69
        cur.execute("UPDATE SoloLeaderboard set score = %s where DiscordId = %s", (newscore, str(Interaction.user.id),))
        conn.commit()
        desc = 'Ese kese package milega'
        ti = 'Gonna cry ?'
        embed = await send_embed(ti, desc)
        await Interaction.edit_original_response(embed=embed)

    cur.execute('Delete from sololevelling where userdisc=%s', (user,))
    conn.commit()


@bot.tree.command(name="solo_top", description="Top 10 leaderboard")
async def solo_top(Interaction: discord.Interaction):
    await Interaction.response.defer()
    cur.execute("SELECT * from SoloLeaderboard order by score desc LIMIT 10")
    rows = cur.fetchall()
    conn.commit()
    s = ""
    x = 1
    for r in rows:
        user = await bot.fetch_user(int(r[0]))
        s = s + str(x) + ". " + str(user) + " : " + str(r[1]) + "\n"
        x += 1
    ti = "Top 10"
    desc = f"{s}"
    embed = await send_embed(ti, desc)
    await Interaction.edit_original_response(embed=embed)


@bot.tree.command(name='handle_identify', description='Identify your handle and get started')
@app_commands.describe(handle_name="Enter the handle name")
async def handle_identify(Interaction: discord.Interaction, handle_name: str):
    await Interaction.response.defer()
    CFID = handle_name
    cur.execute('select * from disc_cf_id where DiscID=%s', (str(Interaction.user.id),))
    conn.commit()
    rows = cur.fetchall()
    if rows:
        ti = 'Already Identified'
        desc = 'The handle is already registered to database to change it to different account use handle_change'
        embed = await send_embed(ti, desc)
        await Interaction.edit_original_response(embed=embed)
        return
    linktouser = "https://codeforces.com/api/user.info?handles=" + CFID
    response = await requests.get(linktouser)
    if response.status_code == 200:
        random_key = random.choice(list(handlesetproblems.keys()))
        embed = await asking_compilation_error(Interaction, CFID, random_key)
        await Interaction.edit_original_response(embed=embed)
        await asyncio.sleep(60)
        linktorecentsub = "https://codeforces.com/api/user.status?handle=" + CFID + "&from=1&count=1"
        response = await requests.get(linktorecentsub)
        if response.status_code == 200:
            data = response.json()
            final_data = data['result'][0]
            if final_data['problem']['name'] == random_key:
                if final_data['verdict'] == 'COMPILATION_ERROR':
                    try:
                        user = str(Interaction.user.id)
                        userid = str(CFID)
                        cur.execute('INSERT INTO disc_cf_id VALUES(%s,%s)', (user, userid,))
                    except Exception as error:
                        desc = f"{Interaction.user.mention} handle has been registerd with {userid} and stop " \
                               f"spamming!!! ) "
                        ti = 'Identification Already successfull'
                        embed = await send_embed(ti, desc)
                        await Interaction.edit_original_response(embed=embed)
                        conn.commit()
                        return
                    conn.commit()
                    desc = f"{Interaction.user.mention} handle has been registerd with {userid}"
                    cur.execute("INSERT INTO SoloLeaderboard values(%s, %s)", (str(Interaction.user.id), 0))
                    cur.execute("INSERT INTO DuelLeaderboard values(%s, %s)", (str(Interaction.user.id), 0))
                    conn.commit()
                    ti = 'Identification Successfull'
                    embed = await send_embed(ti, desc)
                    await Interaction.edit_original_response(embed=embed)
                else:
                    desc = 'Please only submit compilation error'
                    ti = 'Submission Error'
                    embed = send_embed(ti, desc)
                    await Interaction.edit_original_response(embed=embed)
            else:
                desc = 'You are too slow Try completing in 60 seconds'
                ti = 'Timed Out'
                embed = await send_embed(ti, desc)
                await Interaction.edit_original_response(embed=embed)
        else:
            desc = 'please try again later there might be issues with API'
            ti = 'API ERROR'
            embed = embed
            await Interaction.edit_original_response(embed=embed)
    else:
        desc = f'{CFID} mentioned does not exist'
        ti = 'Identification Unsuccessfull'
        embed = await send_embed(ti, desc)
        await Interaction.edit_original_response(embed=embed)


@bot.tree.command(name='handle_change', description='Updates your Codeforces handle ')
@app_commands.describe(handle_name="Enter the handle name")
async def handle_change(Interaction: discord.Interaction, handle_name: str):
    await Interaction.response.defer()
    CFID = handle_name
    cur.execute('select * from disc_cf_id where DiscID=%s', (str(Interaction.user.id),))
    conn.commit()
    rows = cur.fetchall()
    if rows:
        if rows[0][1] == CFID:
            desc = 'Handle is already set to this account'
            ti = 'Same as Old'
            await Interaction.edit_original_response(embed=await send_embed(ti, desc))
            return
        linktouser = "https://codeforces.com/api/user.info?handles=" + CFID
        response = await requests.get(linktouser)
        if response.status_code == 200:
            random_key = random.choice(list(handlesetproblems.keys()))
            embed =await asking_compilation_error(Interaction, CFID, random_key)
            await Interaction.edit_original_response(embed=embed)
            await asyncio.sleep(60)
            linktorecentsub = "https://codeforces.com/api/user.status?handle=" + CFID + "&from=1&count=1"
            response = await requests.get(linktorecentsub)
            if response.status_code == 200:
                data = response.json()
                final_data = data['result'][0]
                if final_data['problem']['name'] == random_key:
                    if final_data['verdict'] == 'COMPILATION_ERROR':
                        user = str(Interaction.user.id)
                        userid = str(CFID)
                        cur.execute('Update disc_cf_id set Cf_ID=%s where DiscID =%s', (userid, str(user),))
                        conn.commit()
                        desc = f"{Interaction.user.mention} handle has changed to {userid}"
                        ti = 'Updation Successfull'
                        embed = await send_embed(ti, desc)
                        await Interaction.edit_original_response(embed=embed)
                    else:
                        desc = 'Please only submit compilation error'
                        ti = 'Submission Error'
                        embed = await send_embed(ti, desc)
                        await Interaction.edit_original_response(embed=embed)
                else:
                    desc = 'You are too slow Try completing in 60 seconds'
                    ti = 'Timed Out'
                    embed =await send_embed(ti, desc)
                    await Interaction.edit_original_response(embed=embed)
            else:
                desc = 'please try again later there might be issues with API'
                ti = 'API ERROR'
                embed = embed
                await Interaction.edit_original_response(embed=embed)
        else:
            desc = 'No User exist with the given codeforces id provided'
            ti = 'No CF handle found'
            await Interaction.edit_original_response(embed=await send_embed(ti, desc))
    else:
        desc = 'Looks like you have not identified yours CF handle yet'
        ti = 'Updation Unsuccesfull'
        await Interaction.edit_original_response(embed= await send_embed(ti, desc))


@bot.tree.command(name='duel_end', description='Ends the duel you are currently in')
async def duel_end(Interaction: discord.Interaction):
    await Interaction.response.defer()
    user = Interaction.user.id
    cur.execute("select * from duelchallenge where user1=%s or user2=%s", (str(user), str(user),))
    conn.commit()
    row = cur.fetchall()
    if not row:
        ti = "ERRROR 404"
        desc = "you are not in any duel"
        await Interaction.edit_original_response(embed=await send_embed(ti, desc))
        return
    else:
        contestid = row[0][2]
        index = row[0][3]
        # create table if not exists disc_cf_id (DiscID text primary key, Cf_ID text)'
        cur.execute("select Cf_ID from disc_cf_id where DiscID=%s", ((row[0][1]),))
        handle1 = cur.fetchall()
        cur.execute("select Cf_ID from disc_cf_id where DiscID=%s", ((row[0][0]),))
        handle2 = cur.fetchall()
        url = f"https://codeforces.com/api/user.status?handle={handle1[0][0]}&from=1&count=10"
        response = await requests.get(url)
        data1 = response.json()
        resultuser1 = data1['result']
        bool1 = 0
        rating = 0
        for res in resultuser1:
            if res['problem']['contestId'] == contestid and res['problem']['index'] == index:
                rating = res['problem']['rating']
                if res['verdict'] == 'OK':
                    bool1 = 1
                    unixt1 = res['creationTimeSeconds']
                    break
        url = f"https://codeforces.com/api/user.status?handle={handle2[0][0]}&from=1&count=10"
        responses = await requests.get(url)
        data2 = responses.json()
        resultuser2 = data2['result']
        bool2 = 0
        for res in resultuser2:
            if res['problem']['contestId'] == contestid and res['problem']['index'] == index:
                rating = res['problem']['rating']
                if res['verdict'] == 'OK':
                    bool2 = 1
                    unixt2 = res['creationTimeSeconds']
                    break

        if bool1 == 1 and bool2 == 1:
            if unixt1 > unixt2:
                handle1 = str(row[0][0])
                handle2 = str(row[0][1])
                cur.execute("SELECT score from DuelLeaderboard where DiscordId = %s", (handle1,))
                score = cur.fetchall()
                newscore = score[0][0] + ((int(rating) // 100) * (int(rating) // 100))
                cur.execute("UPDATE DuelLeaderboard set score = %s where DiscordId = %s",
                            (newscore, handle1,))
                cur.execute("SELECT score from DuelLeaderboard where DiscordId = %s", (handle2,))
                score = cur.fetchall()
                newscore = score[0][0] - ((int(rating) // 100) * (int(rating) // 100))
                cur.execute("UPDATE DuelLeaderboard set score = %s where DiscordId = %s",
                            (newscore, handle2,))
                conn.commit()
                t2 = row[0][4]
                t1 = await unixTimeToHumanReadable(unixt2)
                datetime_str = str(t1[1]) + "/" + str(t1[2]) + "/" + str(t1[0]) + " " + str(t1[3]) + ":" + str(
                    t1[4]) + ":" + str(t1[5])
                datetime_object = datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S')
                time_change = timedelta(hours=5, minutes=30)
                new_time = datetime_object + time_change
                datetime_object1 = datetime.strptime(t2, '%Y-%m-%d %H:%M:%S')
                duration = new_time - datetime_object1

                ti = "RESULT"
                handle1 = await bot.fetch_user(int(handle1))
                desc = str(handle1) + " won and the time taken to solve this problem " + str(duration)
                await Interaction.edit_original_response(embed=await send_embed(ti, desc))
            elif unixt2 > unixt1:
                handle1 = str(row[0][0])
                handle2 = str(row[0][1])
                cur.execute("SELECT score from DuelLeaderboard where DiscordId = %s", (handle1,))
                score = cur.fetchall()
                newscore = score[0][0] - ((int(rating) // 100) * (int(rating) // 100))
                cur.execute("UPDATE DuelLeaderboard set score = %s where DiscordId = %s",
                            (newscore, handle1,))
                cur.execute("SELECT score from DuelLeaderboard where DiscordId = %s", (handle2,))
                score = cur.fetchall()
                newscore = score[0][0] + ((int(rating) // 100) * (int(rating) // 100))
                cur.execute("UPDATE DuelLeaderboard set score = %s where DiscordId = %s",
                            (newscore, handle2,))
                conn.commit()
                t2 = row[0][4]
                t1 = await unixTimeToHumanReadable(unixt1)
                datetime_str = str(t1[1]) + "/" + str(t1[2]) + "/" + str(t1[0]) + " " + str(t1[3]) + ":" + str(
                    t1[4]) + ":" + str(t1[5])
                datetime_object = datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S')
                time_change = timedelta(hours=5, minutes=30)
                new_time = datetime_object + time_change
                datetime_object1 = datetime.strptime(t2, '%Y-%m-%d %H:%M:%S')
                duration = new_time - datetime_object1
                ti = "RESULT"

                handle2 = await bot.fetch_user(int(handle2))
                desc = str(handle2) + " won and the time taken to solve this problem " + str(duration)
                await Interaction.edit_original_response(embed=await send_embed(ti, desc))
            else:
                ti = "RESULT"
                desc = "draw"
                await Interaction.edit_original_response(embed=await send_embed(ti, desc))
            cur.execute("delete from duelchallenge where user1=%s or user2=%s", (str(row[0][1]), str(row[0][1]),))
            conn.commit()
        elif bool1 == 1:
            handle1 = str(row[0][0])
            handle2 = str(row[0][1])
            cur.execute("SELECT score from DuelLeaderboard where DiscordId = %s", (handle1,))
            score = cur.fetchall()
            newscore = score[0][0] - ((int(rating) // 100) * (int(rating) // 100))
            cur.execute("UPDATE DuelLeaderboard set score = %s where DiscordId = %s",
                        (newscore, handle1,))
            cur.execute("SELECT score from DuelLeaderboard where DiscordId = %s", (handle2,))
            score = cur.fetchall()
            newscore = score[0][0] + ((int(rating) // 100) * (int(rating) // 100))
            cur.execute("UPDATE DuelLeaderboard set score = %s where DiscordId = %s",
                        (newscore, handle2,))
            conn.commit()
            t2 = row[0][4]
            t1 = await unixTimeToHumanReadable(unixt1)
            datetime_str = str(t1[1]) + "/" + str(t1[2]) + "/" + str(t1[0]) + " " + str(t1[3]) + ":" + str(
                t1[4]) + ":" + str(t1[5])
            datetime_object = datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S')
            time_change = timedelta(hours=5, minutes=30)
            new_time = datetime_object + time_change
            datetime_object1 = datetime.strptime(t2, '%Y-%m-%d %H:%M:%S')
            duration = new_time - datetime_object1
            ti = "RESULT"
            handle2 = await bot.fetch_user(int(handle2))
            desc = str(handle2) + " won and the time taken to solve this problem " + str(duration)
            await Interaction.edit_original_response(embed=await send_embed(ti, desc))
            cur.execute("delete from duelchallenge where user1=%s or user2=%s", (str(row[0][1]), str(row[0][1]),))
            conn.commit()
        elif bool2 == 1:
            handle1 = str(row[0][0])
            handle2 = str(row[0][1])
            cur.execute("SELECT score from DuelLeaderboard where DiscordId = %s", (handle1,))
            score = cur.fetchall()
            newscore = score[0][0] + ((int(rating) // 100) * (int(rating) // 100))
            cur.execute("UPDATE DuelLeaderboard set score = %s where DiscordId = %s",
                        (newscore, handle1,))
            cur.execute("SELECT score from DuelLeaderboard where DiscordId = %s", (handle2,))
            score = cur.fetchall()
            newscore = score[0][0] - ((int(rating) // 100) * (int(rating) // 100))
            cur.execute("UPDATE DuelLeaderboard set score = %s where DiscordId = %s",
                        (newscore, handle2,))
            conn.commit()
            t2 = row[0][4]
            t1 =await unixTimeToHumanReadable(unixt2)
            datetime_str = str(t1[1]) + "/" + str(t1[2]) + "/" + str(t1[0]) + " " + str(t1[3]) + ":" + str(
                t1[4]) + ":" + str(t1[5])
            datetime_object = datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S')
            time_change = timedelta(hours=5, minutes=30)
            new_time = datetime_object + time_change
            datetime_object1 = datetime.strptime(t2, '%Y-%m-%d %H:%M:%S')
            duration = new_time - datetime_object1

            ti = "RESULT"
            handle1 = await bot.fetch_user(int(handle1))
            desc = str(handle1) + " won and the time taken to solve this problem " + str(duration)
            await Interaction.edit_original_response(embed=await send_embed(ti, desc))
            cur.execute("delete from duelchallenge where user1=%s or user2=%s", (str(row[0][1]), str(row[0][1]),))
            conn.commit()
        else:
            ti = "DRAW ?"
            handle_name = row[0][0]
            print(handle_name)
            if str(Interaction.user.id) == row[0][0]:
                handle_name = row[0][1]
            handle_name1 = await bot.fetch_user(handle_name)
            desc = f"{handle_name1.mention}You have been offered a draw"
            await Interaction.edit_original_response(embed=await send_embed(ti, desc),
                                                     view=ButtonYesNoduel_end(Interaction, 30, handle_name))


@bot.tree.command(name='handle_set', description='Set handle manually(only mod)')
async def handle_set(Interaction: discord.Interaction, disc_id: discord.Member, handle: str):
    await Interaction.response.defer()
    linktouser = "https://codeforces.com/api/user.info?handles=" + handle
    response = await requests.get(linktouser)
    if response.status_code == 200:
        cur.execute("Select * from disc_cf_id where DiscID=%s", (str(disc_id.id),))
        conn.commit()
        rows = cur.fetchall()
        if rows:
            await Interaction.edit_original_response(embed=await send_embed("Problem", "Handle already set "))
            return
        cur.execute("Insert into disc_cf_id values (%s,%s)", (str(disc_id.id), str(handle),))
        conn.commit()
        cur.execute("INSERT INTO SoloLeaderboard values(%s, %s)", (str(disc_id.id), 0))
        cur.execute("INSERT INTO DuelLeaderboard values(%s, %s)", (str(disc_id.id), 0))
        conn.commit()
        await Interaction.edit_original_response(
            embed=await send_embed("Handle Identified", f"Handle Identified Successfully for {disc_id.mention} to {handle}"))
    else:
        await Interaction.edit_original_response(embed=await send_embed("Try Again", "Handle does not exist try again"))


@bot.tree.command(name='duel_challenge', description='Challenge other user for a 1v1 battle')
@app_commands.describe(handle_name="Mention the discord ID of user you want to battle")
async def duel_challenge(Interaction: discord.Interaction, handle_name: discord.Member, rating: int = None):
    await Interaction.response.defer()
    if Interaction.user.id == handle_name.id:
        ti = "Cannot challenge yourself"
        desc = f"Lonely? Try solo"
        await Interaction.edit_original_response(embed=await send_embed(ti, desc))
        return
    cur.execute("select Cf_ID from disc_cf_id where DiscID=%s", (str(Interaction.user.id),))
    conn.commit()
    global duelrating
    duelrating = rating
    row = cur.fetchall()
    if not row:
        await Interaction.edit_original_response(embed=await send_embed("Handle not identified",
                                                                 f"Looks like {Interaction.user.mention} has not "
                                                                 f"identified handle"))
        return
    cur.execute("Select Cf_ID from disc_cf_id where DiscID=%s", (str(handle_name.id),))
    conn.commit()
    rows = cur.fetchall()
    if not rows:
        await Interaction.edit_original_response(
            embed=await send_embed("Handle not identified", f"Looks like {handle_name.mention} has not identified handle"))
        return
    if duelrating is not None and (duelrating < 800 or duelrating > 3500 or duelrating % 100 != 0):
        await Interaction.edit_original_response("Rating dhang se daal")
        return
    cur.execute('select * from duelchallenge where user1=%s or user2=%s or user2=%s or user1 =%s',
                (str(Interaction.user.id), str(handle_name.id), str(Interaction.user.id), str(handle_name.id),))
    conn.commit()
    rowsy = cur.fetchall()
    if rowsy:
        # user1= row[0][0]
        # user2=row[1][1]
        # user3=row[0][1]
        # user4=row[1][0]

        await Interaction.edit_original_response(
            embed=await send_embed("Cant be done", "One of the user is already in a duel "))
        return
    desc = f"{handle_name.mention} you are being challenged by {Interaction.user.mention}"
    ti = f"Lets Battle it out"
    await Interaction.edit_original_response(embed=await send_embed(ti, desc), view=ButtonYesNo(Interaction, 30, handle_name))


@bot.tree.command(name='my_duel_rank', description='Gives your duel rank')
async def my_duel_rank(Interaction: discord.Interaction):
    await Interaction.response.defer()
    user = Interaction.user.id
    cur.execute('Select * from DuelLeaderboard order by score DESC')
    conn.commit()
    rows = cur.fetchall()
    count = 0

    for row in rows:
        count += 1
        if row[0] == str(user):
            desc = f"Your rank is {count} with a score of {row[1]}"
            ti = "Duel Rank!"
            await Interaction.edit_original_response(embed=await send_embed(ti, desc))
            return
    desc = f"You have never been in a duel"
    ti = "No duel record found"
    await Interaction.edit_original_response(embed=await send_embed(ti, desc))


@bot.tree.command(name='my_solo_rank', description='Gives your solo rank')
async def my_solo_rank(Interaction: discord.Interaction):
    await Interaction.response.defer()
    user = Interaction.user.id
    cur.execute('Select * from SoloLeaderboard order by score DESC')
    conn.commit()
    rows = cur.fetchall()
    count = 0
    for row in rows:
        count += 1
        if row[0] == str(user):
            desc = f"Your rank is {count} with a score of {row[1]}"
            ti = "Solo Rank!"
            await Interaction.edit_original_response(embed=await send_embed(ti, desc))
            return
    desc = f"You have never been in a solo"
    ti = "No solo record found"
    await Interaction.edit_original_response(embed=await send_embed(ti, desc))


@bot.tree.command(name='daily_problem', description='isse MODS daily problems bhejenge :)')
async def daily_problem(Interaction: discord.Interaction, contestid: str, contestindex: str):
    await Interaction.response.defer()
    if Interaction.channel_id != 1056929299501953104:
        await Interaction.edit_original_response(
            content="This command cannot be used here OR you are not the chosen one ", ephemeral=True)
        return
    link = f"https://codeforces.com/problemset/problem/{contestid}/{contestindex}"

    emoji = "✅"
    await Interaction.edit_original_response(f"{link}")
    mes = await Interaction.original_response()
    print(type(mes))
    print(mes.id)
    cur.execute('truncate table reactions')
    cur.execute("INSERT into reactions values(%s)", (mes.id,))
    conn.commit()
    await mes.add_reaction(emoji)


@bot.tree.command(name='reaction', description='isse MODS daily problems ke reactions lenge :)')
async def reaction(Interaction: discord.Interaction):
    await Interaction.response.defer()
    cur.execute("SELECT * from reactions")
    row = cur.fetchall()
    conn.commit()
    mes_id = int(row[0][0])
    channel_id = 1056929299501953104
    channel = bot.get_channel(channel_id)
    message = await channel.fetch_message(mes_id)
    users = []
    for r in message.reactions:
        async for user in r.users():
            users.append(str(user.name) + "#" + str(user.discriminator))
    await Interaction.edit_original_response(f"{users}")


@bot.tree.command(name='mashup', description='Upto 5 users get a custom contest where you can participate')
@app_commands.describe(div="2/3/4")
async def mashup(Interaction: discord.Interaction, p1: str, div: int):
    await Interaction.response.defer()

    users = p1.split(" ")
    userlist = []
    for user in users:
        x = int(user[2:len(user) - 1])
        userlist.append(str(x))

    userlist.append(str(Interaction.user.id))
    for user in userlist:
        cur.execute('select Cf_id from disc_cf_id where DiscID =%s', (str(user),))
        conn.commit()
        row1 = cur.fetchall()
        if not row1:
            ti = "Handle unidentified"
            userw = await bot.fetch_user(user)
            desc = f"Handle for {userw.mention} is not identified please use  /handle_identify"
            await Interaction.edit_original_response(embed=await send_embed(ti, desc))
            return
    problemset = []

    for user in userlist:
        print(user)
        cur.execute('select Cf_id from disc_cf_id where DiscID =%s', (str(user),))
        row = cur.fetchall()
        handle = str(row[0][0])
        print(handle)
        pr = await get_user_problems(handle)
        problemset = pr + problemset

    conn.commit()
    print(len(problemset))
    if div == 2:
        rating1 = random.choice([800, 900, 1000])
        rating2 = random.choice([1000, 1100, 1200])
        rating3 = random.choice([1200, 1300, 1400])
        rating4 = random.choice([1500, 1600, 1700])
        rating5 = random.choice([1700, 1800, 1900])
        rating6 = random.choice([2000, 2100, 2200])
        list = []
        problem1 = random.choice(await get_user_unsolved_problems(problemset, rating1, list))
        problem2 = random.choice(await get_user_unsolved_problems(problemset, rating2, list))
        problem3 = random.choice(await get_user_unsolved_problems(problemset, rating3, list))
        problem4 = random.choice(await get_user_unsolved_problems(problemset, rating4, list))
        problem5 = random.choice(await get_user_unsolved_problems(problemset, rating5, list))
        problem6 = random.choice(await get_user_unsolved_problems(problemset, rating6, list))
        link1 = "https://codeforces.com/contest/" + str(problem1[0]) + "/problem/" + str(problem1[1])
        link2 = "https://codeforces.com/contest/" + str(problem2[0]) + "/problem/" + str(problem2[1])
        link3 = "https://codeforces.com/contest/" + str(problem3[0]) + "/problem/" + str(problem3[1])
        link4 = "https://codeforces.com/contest/" + str(problem4[0]) + "/problem/" + str(problem4[1])
        link5 = "https://codeforces.com/contest/" + str(problem5[0]) + "/problem/" + str(problem5[1])
        link6 = "https://codeforces.com/contest/" + str(problem6[0]) + "/problem/" + str(problem6[1])
        ti = "LessGoooo"
        desc = f" A. [{problem1[2]}]({link1}) \n B. [{problem2[2]}]({link2}) \n C. [{problem3[2]}]({link3}) \n D. " \
               f"[{problem4[2]}]({link4}) \n E. [{problem5[2]}]({link5}) \n F. [{problem6[2]}]({link6}) "
        embebd = await send_embed(ti, desc)

        await Interaction.edit_original_response(embed=embebd)
    elif div == 3:
        rating1 = random.choice([800, 900])
        rating2 = random.choice([900, 1000])
        rating3 = random.choice([1100, 1200, 1300])
        rating4 = random.choice([1300, 1400])
        rating5 = random.choice([1400, 1500, 1600])
        rating6 = random.choice([1700, 1800])
        list = []
        problem1 = random.choice(await get_user_unsolved_problems(problemset, rating1, list))
        problem2 = random.choice(await get_user_unsolved_problems(problemset, rating2, list))
        problem3 = random.choice(await get_user_unsolved_problems(problemset, rating3, list))
        problem4 = random.choice(await get_user_unsolved_problems(problemset, rating4, list))
        problem5 = random.choice(await get_user_unsolved_problems(problemset, rating5, list))
        problem6 = random.choice(await get_user_unsolved_problems(problemset, rating6, list))
        link1 = "https://codeforces.com/contest/" + str(problem1[0]) + "/problem/" + str(problem1[1])
        link2 = "https://codeforces.com/contest/" + str(problem2[0]) + "/problem/" + str(problem2[1])
        link3 = "https://codeforces.com/contest/" + str(problem3[0]) + "/problem/" + str(problem3[1])
        link4 = "https://codeforces.com/contest/" + str(problem4[0]) + "/problem/" + str(problem4[1])
        link5 = "https://codeforces.com/contest/" + str(problem5[0]) + "/problem/" + str(problem5[1])
        link6 = "https://codeforces.com/contest/" + str(problem6[0]) + "/problem/" + str(problem6[1])
        ti = "LessGoooo"
        desc = f" A. [{problem1[2]}]({link1}) \n B. [{problem2[2]}]({link2}) \n C. [{problem3[2]}]({link3}) \n D. " \
               f"[{problem4[2]}]({link4}) \n E. [{problem5[2]}]({link5}) \n F. [{problem6[2]}]({link6})"
        embebd =await send_embed(ti, desc)

        await Interaction.edit_original_response(embed=embebd)
    elif div == 1:
        await Interaction.edit_original_response(content="Coming up soon")
    elif div == 4:
        rating1 = random.choice([800, 900])
        rating2 = random.choice([800, 900])
        rating3 = random.choice([1000, 1100])
        rating4 = random.choice([1100, 1200])
        rating5 = random.choice([1200, 1300])
        rating6 = random.choice([1400, 1500])
        list = []
        problem1 = random.choice(await get_user_unsolved_problems(problemset, rating1, list))
        problem2 = random.choice(await get_user_unsolved_problems(problemset, rating2, list))
        problem3 = random.choice(await get_user_unsolved_problems(problemset, rating3, list))
        problem4 = random.choice(await get_user_unsolved_problems(problemset, rating4, list))
        problem5 = random.choice(await get_user_unsolved_problems(problemset, rating5, list))
        problem6 = random.choice(await get_user_unsolved_problems(problemset, rating6, list))
        link1 = "https://codeforces.com/contest/" + str(problem1[0]) + "/problem/" + str(problem1[1])
        link2 = "https://codeforces.com/contest/" + str(problem2[0]) + "/problem/" + str(problem2[1])
        link3 = "https://codeforces.com/contest/" + str(problem3[0]) + "/problem/" + str(problem3[1])
        link4 = "https://codeforces.com/contest/" + str(problem4[0]) + "/problem/" + str(problem4[1])
        link5 = "https://codeforces.com/contest/" + str(problem5[0]) + "/problem/" + str(problem5[1])
        link6 = "https://codeforces.com/contest/" + str(problem6[0]) + "/problem/" + str(problem6[1])
        ti = "LessGoooo"
        desc = f" A. [{problem1[2]}]({link1}) \n B. [{problem2[2]}]({link2}) \n C. [{problem3[2]}]({link3}) \n D. " \
               f"[{problem4[2]}]({link4}) \n E. [{problem5[2]}]({link5}) \n F. [{problem6[2]}]({link6})"
        embebd =await send_embed(ti, desc)

        await Interaction.edit_original_response(embed=embebd)
    else:
        await Interaction.edit_original_response(content="Unable to find easier problems than div4")


@bot.tree.command(name='graph_compare', description='Mention Discord Ids of whom you want to compare rating curve')
async def graph_compare(Interaction: discord.Interaction, p1: str):
    await Interaction.response.defer()
    users = p1.split(" ")
    userlist = []
    for user in users:
        x = int(user[2:len(user) - 1])
        userlist.append(str(x))

    mainlist = []
    userlist.append(str(Interaction.user.id))
    for user in userlist:
        cur.execute('select Cf_id from disc_cf_id where DiscID =%s', (str(user),))
        conn.commit()
        row1 = cur.fetchall()
        if not row1:
            ti = "Handle unidentified"
            desc = f"Handle for {user.mention} is not identified please use  /handle_identify"
            await Interaction.edit_original_response(embed=await send_embed(ti, desc))
            return
        mainlist.append(row1[0][0])

    problemset = []

    for handle in mainlist:
        print(handle)
        link = "https://codeforces.com/api/user.rating?handle="
        link += handle
        print(link)
        responses = await requests.get(link)
        details_api = {}
        for page in responses:
            if page.request.url == link:
                details_api = page.json()
        details_api = details_api['result']
        newrat = []
        date = []
        for newrating in details_api:
            newrat.append(newrating["newRating"])

        for dates in details_api:
            date.append(datetime.strptime(await unixTimeToHumanReadableVaibhav(dates["ratingUpdateTimeSeconds"]), "%Y-%m-%d"))

        dates = matplotlib.dates.date2num(date)
        matplotlib.pyplot.plot_date(dates, newrat, linestyle='solid', label=handle)
        matplotlib.pyplot.legend()
        matplotlib.pyplot.xlabel("time")
        matplotlib.pyplot.ylabel("rating")
        # plt.title(f'{ctx.message.author}\'s Graph')
        matplotlib, pyplot.savefig(fname='plot')
        # os.remove('plot.png')
    await Interaction.edit_original_response(attachments=[discord.File('plot.png')])
    matplotlib.pyplot.clf()
    os.remove('plot.png')


# # @bot.command(name="contest")
# # async def _command(ctx):
# #     channel = ctx.channel
# #     react = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]

# #     mes = await channel.send('Div?')
# #     for tmp in react:
# #         await mes.add_reaction(tmp)

# #     def check(reaction, user):
# #         return user == ctx.author and str(reaction.emoji) in react

# #     try:
# #         reaction, user = await bot.wait_for('reaction_add', timeout=10.0, check=check)
# #     except asyncio.TimeoutError:
# #         await channel.send('Kaanp kahe rahi ho?')
# #     else:
# #         i = react.index(str(reaction))
# #         if i == 0:
# #             await channel.send('Div 2 dede chup chaap!')
# #         else:
# #             rating = \
# #                 [[[800, 900], [800, 800], [800, 800]],
# #                 [[1100, 1200], [900, 1000], [800, 900]],
# #                 [[1300, 1500], [1200, 1300], [900, 1100]],
# #                 [[1600, 1800], [1400, 1600], [1200, 1300]],
# #                 [[1900, 2100], [1700, 1800], [1400, 1600]]]
# #             i -= 1
# #             for problem in rating:
# #                 await channel.send(str(problem[i]) + '\n')
intents = discord.Intents.default()
intents.all()

# Create the Discord client instance
client = discord.Client(intents=intents)


# Fetch the token from the 'TOKEN' environment variable
tokenval = os.environ.get('token')
bot.run(tokenval)
