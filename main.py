import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from datetime import datetime, time
from pytz import timezone

#configurations
TEAM = "DEAL"  #switch between DEAL and OPS
ENV = "PROD"  #switch between TEST and PROD

OP_TEAM = {
  1670599682: 'Lucas',
  2024196719: 'Mads',
  1772194299: 'Calvin',
  2141305286: 'Alex',
  5302402652: 'Naomi',
  5531916446: 'Sally',
  1709343997: 'Tony',
  5678699846: 'Silvia',
  5397524528: 'Darrell',
  1642785798: 'Andrew',
  5773868434: 'Tina',
  5624281247: 'Moon',
  1332886084: 'Ryan'
}

DEAL_TEAM = [2024196719, 5302402652, 2141305286, 1332886084]
OPS_TEAM = [1709343997, 5678699846, 5397524528, 5773868434, 5624281247]
ADMIN = [1670599682]

#define global variables
chat_id = ""
current_team = []
daily_update_missing = []
daily_update_done = []
reminder_date = datetime.now(timezone('EST'))
reminder_msgid = 0

logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  level=logging.INFO)

#Start of code


def lookup(user_id):
  return OP_TEAM[user_id]


def mention(user_id):
  return '<a href="tg://user?id=' + str(
    user_id) + '">@' + OP_TEAM[user_id] + '</a>'


def print_stats(step):
  print("--------------------")
  print("System stats @" + step)
  print(reminder_date)
  print(reminder_msgid)
  print('current team:' + str(current_team))
  print('done:' + str(daily_update_done))
  print('missing:' + str(daily_update_missing))
  print("--------------------")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if update.effective_user.id in ADMIN:
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="I'm OP Crypto Bot in the chat:" +
                                   str(update.effective_chat.id))
  else:
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='No permission')


async def myID(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='UserID:' +
                                 str(update._effective_user.id))


async def manual_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):

  if update.effective_user.id in ADMIN:
    global daily_update_missing, daily_update_done, reminder_date

    #generate reminder for the new day
    daily_update_missing = current_team[:]
    daily_update_done = []
    reminder_date = datetime.now(timezone('EST'))

    print_stats("manual reminder initialization")

    await generate_reminder(update.effective_chat.id, context)
  else:
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='No permission')


async def manual_reminder2(update: Update, context: ContextTypes.DEFAULT_TYPE):

  if update.effective_user.id in ADMIN:

    print_stats("manual reminde2")
    print("Sending reminder for below")
    print(daily_update_missing)

    if daily_update_missing:
      await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="❗Pending: " + ' '.join(map(mention, daily_update_missing)),
        parse_mode='HTML',
        reply_to_message_id=reminder_msgid)

  else:
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='No permission')


async def callback_daily_reminder(context: ContextTypes.DEFAULT_TYPE):
  global daily_update_missing, daily_update_done, reminder_date

  #generate reminder for the new day
  daily_update_missing = current_team[:]
  daily_update_done = []
  reminder_date = datetime.now(timezone('EST'))

  print_stats("callback reminder initialization")

  await generate_reminder(chat_id, context)


async def callback_daily_reminder2(context: ContextTypes.DEFAULT_TYPE):

  print_stats("callback reminder2")
  print("Sending reminder for below")
  print(daily_update_missing)

  if daily_update_missing:
    await context.bot.send_message(
      chat_id=chat_id,
      text="❗Pending: " + ' '.join(map(mention, daily_update_missing)),
      parse_mode='HTML',
      reply_to_message_id=reminder_msgid)


async def generate_reminder(chat_id: int, context: ContextTypes.DEFAULT_TYPE):

  global reminder_msgid

  if daily_update_missing:
    m = await context.bot.send_message(
      chat_id=chat_id,
      text='<b>Daily team updates (' + reminder_date.strftime("%b %-d") +
      ')</b>\n✅Submitted: ' + ', '.join(map(lookup, daily_update_done)) +
      '\n❗Pending: ' + ', '.join(map(lookup, daily_update_missing)),
      parse_mode='HTML')
    reminder_msgid = m.message_id

    await context.bot.send_message(chat_id=chat_id,
                                   text=' '.join(
                                     map(mention, daily_update_missing)),
                                   parse_mode='HTML')

  else:
    m = await context.bot.send_message(
      chat_id=chat_id,
      text='<b>Daily team updates (' + reminder_date.strftime("%b %-d") +
      ')</b>\n✅ All Submitted: ' + ', '.join(map(lookup, daily_update_done)),
      parse_mode='HTML')
    reminder_msgid = m.message_id


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if update.effective_user.id in ADMIN:
    print_stats()
  else:
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='No permission')


async def update(update: Update, context: ContextTypes.DEFAULT_TYPE):
  id = update.effective_user.id
  #await context.bot.send_message(chat_id=update.effective_chat.id,
  #                               text=' '.join(context.args))

  print("ID = " + str(id))
  print_stats("Pre-update")

  #user has not submitted updates before
  if id in daily_update_missing:
    print("Updating records")
    daily_update_done.append(id)
    daily_update_missing.remove(id)
    await generate_reminder(update.effective_chat.id, context)

  print_stats("Post-update")


if __name__ == '__main__':

  print("Start main function")
  token_id = os.getenv("TELEGRAM_TOKEN_" + ENV)
  chat_id = os.getenv("CHAT_ID_" + ENV)
  application = ApplicationBuilder().token(token_id).build()

  if TEAM == 'DEAL':
    current_team = DEAL_TEAM[:]
  elif TEAM == 'OPS':
    current_team = OPS_TEAM[:]
  else:
    current_team = []

  job_queue = application.job_queue

  #job_minute = job_queue.run_repeating(callback_minute, interval=60, first=10)
  job_update_reminder = job_queue.run_daily(
    callback_daily_reminder, time(22, 0, 0, tzinfo=timezone('US/Eastern')),
    (1, 2, 3, 4, 5))

  job_update_reminder2 = job_queue.run_daily(
    callback_daily_reminder2, time(10, 0, 0, tzinfo=timezone('US/Eastern')),
    (2, 3, 4, 5, 6))

  reminder_handler = CommandHandler('mr', manual_reminder)
  reminder_handler2 = CommandHandler('mr2', manual_reminder2)
  stats_handler = CommandHandler('stats', stats)
  userid_handler = CommandHandler('myID', myID)
  start_handler = CommandHandler('start', start)
  update_handler = CommandHandler('update', update)

  application.add_handler(reminder_handler)
  application.add_handler(reminder_handler2)
  application.add_handler(stats_handler)
  application.add_handler(userid_handler)
  application.add_handler(start_handler)
  application.add_handler(update_handler)

  print_stats("initialization")

  application.run_polling()
