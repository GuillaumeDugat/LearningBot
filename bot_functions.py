import random
import time

from database_manager import *

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('''
This bot helps you to learn a new language. Here's a list of what you can do :
    /create `name` : `desc`- Create a new deck whose name is `name` and description is `desc`
    /workingDeckName - Print the name of the current working deck
    /add `word` : `translation` - Add a new card to the working deck
    /move `name` - Change the working deck
    /seq (`nbr`) : launch a sequence of words (no argument = all the words, `nbr` = size of the sequence)
''')

def start(update, context):
    """First command that is run when a new user start using the bot."""
    id_user = update.message.from_user.id
    username = update.message.from_user.username
    add_user_to_db(id_user, username)
    update.message.reply_text("Welcome !")

def create_deck(update, context):
    """Create a new deck by a name and a description"""
    args = " ".join(context.args).split(" : ", 1)
    name = args[0]
    if len(name) == 0:
        update.message.reply_text("You must enter a name for your deck")
    else:
        if len(args) == 1:
            desc = ""
        else:
            desc = args[1]
        id_user = update.message.from_user.id
        id_deck = add_deck_to_db(id_user, name, desc)
        if id_deck == None:
            update.message.reply_text("This name is already used for a deck, retry with a new one") 
        else:    
            update.message.reply_text("Your deck has been successfully created")
            update_working_deck_id(id_user, id_deck)
            update.message.reply_text("You move to deck " + name)    

def working_deck_name(update, context):
    """Return the name of the current working deck."""
    id_user = update.message.from_user.id
    working_deck_id = find_working_deck_id(id_user)
    if working_deck_id == None:
        update.message.reply_text("No working deck")
    else:
        deck = find_deck_by_id(working_deck_id)
        update.message.reply_text("Working deck : {}".format(deck["name"]))

def change_working_deck(update, context):
    """Enable to change the current working deck."""
    name = " ".join(context.args)
    id_user = update.message.from_user.id
    id_deck = find_deck_by_name(id_user, name)
    if len(name) == 0:
        update.message.reply_text("You must enter a name")
    elif id_deck == None:
        update.message.reply_text("Deck's name not found")
    else:
        update_working_deck_id(id_user, id_deck)
        update.message.reply_text("You move to deck " + name)

def add_card(update, context):
    """Add a new card (a couple of a word and its translation to the working deck."""
    args = " ".join(context.args).split(" : ", 1)
    id_user = update.message.from_user.id
    working_deck_id = find_working_deck_id(id_user)      
    if working_deck_id == None:
        update.message.reply_text("You must create a deck")
    elif len(args) == 1:
        update.message.reply_text("You must add a translation")
    else:
        word = args[0]
        translated_word = args[1]
        add_card_to_db(id_user, working_deck_id, word, translated_word)
        update.message.reply_text("It has been successfully added")

def sequence(update, context):
    """Launch a sequence of words of the working deck."""
    arg = " ".join(context.args)
    id_user = update.message.from_user.id
    working_deck_id = find_working_deck_id(id_user)
    if working_deck_id == None:
        update.message.reply_text("You must create a deck")
    else:
        cards = list_of_cards(working_deck_id)
        if len(cards) == 0:
            update.message.reply_text("No cards in the working deck")
        elif arg == "": # select all the cards in a random order
            selection = random.sample(cards, len(cards))
            add_sequence_to_db(id_user, selection)
            next_word(update, context)
        else:
            try:
                n = int(arg)
                assert n > 0
            except ValueError:
                update.message.reply_text("Invalid argument : you must enter an integer")
            except AssertionError:
                update.message.reply_text("Invalid argument : you must enter a positiv integer")
            else:
                selection = [random.choice(cards) for _ in range(n)]
                add_sequence_to_db(id_user, selection)
                next_word(update, context)

def next_word(update, context):
    """Ask to guess the next word of the list of the sequence."""
    id_user = update.message.from_user.id
    sequence_list = get_sequence_list(id_user)
    if len(sequence_list) == 0:
        update.message.reply_text("You have just finished your sequence !")
    else:
        _, _, translated_word = sequence_list[0]
        update.message.reply_text(translated_word)

def answer(update, context):
    """Take into account the answer (activated when the user answers without command."""
    id_user = update.message.from_user.id
    sequence_list = get_sequence_list(id_user)    
    if len(sequence_list) != 0:
        ans = update.message.text
        id_seq, correct_word, _ = sequence_list[0]
        remove_sequence_card(id_seq)
        if correct_word != ans:
            update.message.reply_text("The correct answer was : " + correct_word)
            time.sleep(1)
        next_word(update, context)
