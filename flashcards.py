
from typing import List
import os, sys, argparse



class LoggerOut:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.filename = filename

    def write(self, message):
        self.terminal.write(message)
        with open(self.filename, "a") as file:
            print(message, file=file, flush=True, end='')

    def flush(self):
        pass


class LoggerIn:
    def __init__(self, filename):
        self.terminal = sys.stdin
        self.filename = filename

    def readline(self):
        entry = self.terminal.readline()
        with open(self.filename, "a") as file:
            print(entry.rstrip(), file=file, flush=True)
        return entry


class Card:
    '''
    Individual cards are created with a term and definition, and mistakes
    initialized at 0
    '''

    def __init__(self, term: str, definition: str, mistakes=0) -> None:
        self.term = term
        self.definition = definition
        self.mistakes = mistakes

    def __str__(self) -> str:
        return f'{self.term}:{self.definition}'

    def just_term(self) -> str:
        return f'{self.term}'

    def add_mistake(self):
        self.mistakes += 1

    def reset(self):
        self.mistakes = 0


class Deck:
    '''
    A Deck is a collection (list) of cards. Creating a new deck creates an empty list.
    '''
    def __init__(self):
        self.cards = []

    def has_term(self, term: str):
        '''
        Returns True if the deck contains a card with the given term
        '''
        for card in self.cards:
            return term == card.term

    def has_def(self, definition: str):
        '''
        Returns True if the deck contains a card with the given definition
        '''
        for card in self.cards:
            return definition == card.definition


    def add_card(self, card: Card):
        '''
        Adds a card to the deck
        '''
        self.cards.append(card)
        #print(f'The pair ("{card}") has been added.\n')

    def remove_card(self, term: str):
        '''
        Removes a card from the deck
        '''
        for card in self.cards:
            if card.term == term:
                self.cards.remove(card)
        print('The card has been removed')


    def size(self) -> int:
        '''
        Return the size of the deck
        '''
        return len(self.cards)


    def definitions(self) -> List[str]:
        '''
        Return a list of the definitions for each card in the deck
        '''
        return [x.definition for x in self.cards]


    def get_term(self, definition: str) -> str:
        '''
        Given a definition of a card, return the term associated
        with that definition
        '''
        for card in self.cards:
            if card.definition == definition:
                return card.term

    def most_mistakes(self) -> int:
        mistakes = [x.mistakes for x in self.cards]
        #print(len(mistakes))
        return max(mistakes)


    def hardest_card(self) -> List[Card]:
        hardest_cards = [x for x in self.cards if x.mistakes == self.most_mistakes()]
        hardest_cards = list(filter(lambda x: x.mistakes != 0, hardest_cards))
        #for card in hardest_cards:
        #    print(card, type(card))
        return hardest_cards


    def clear(self)-> None:
        self.cards = []



# EXCEPTIONS  *********************************************

class TermAlreadyExistsError(Exception):
    pass

class DefinitionAlreadyExistsError(Exception):
    pass

class InvalidChoiceError(Exception):
    pass

class NoSuchCardError(Exception):
    pass


# FUNCTIONS ***************************************


def menu() -> str:
    '''
    The user is given a list of choices to drive the program. Only valid choices (exactly
    as they appear in the list) are allowed. Returns the 'command' from the user.
    '''
    choices = ('add', 'remove', 'import', 'export', 'ask', 'exit', 'log', 'hardest card', 'reset stats')
    message = "Input the action ("+', '.join(choices)+'): '
    print(message)
    while True:
        try:
            command = input()
            if command not in choices:
                raise InvalidChoiceError
            else:
                return command
        except InvalidChoiceError:
            print("Invalid Choice. Try again.")


def add(deck: Deck) -> None:
    '''
    Given a Deck object, this function uses the get_term and get_def functions to
    secure valid term:definition pairs and creates a new card. The card is added
    to the deck.
    '''
    print('The card: ')
    term = get_term(deck)
    print('The definition of the card: ')
    definition = get_def(deck)
    new_card = Card(term, definition)
    deck.add_card(new_card)
    print(f'The pair ("{new_card}") has been added.\n')



def get_term(deck: Deck) -> str:
    '''
    Gets a 'term' from the user. If this term does not exist on a card in the deck,
    the term is returned. Otherwise, TermAlreadyExistsError is raised.
    '''
    while True:
        try:
            term = input()
            if deck.has_term(term):
                raise TermAlreadyExistsError
            else:
                return term
        except TermAlreadyExistsError:
            print(f'The term "{term}" already exists. Try again:')



def get_def(deck: Deck) -> str:
    '''
    Accepts a 'definition' from the user, and checks if any cards in the deck
    already contain this definition. If so, a DefinitionAlreadyExistsError is raised.
    Otherwise, returns the definition.
    '''
    while True:
        try:
            definition = input()
            if deck.has_def(definition):
                raise DefinitionAlreadyExistsError
            else:
                return definition
        except DefinitionAlreadyExistsError:
            print(f'The definition "{definition}" already exists. Try again:')


def remove(deck: Deck) -> None:
    '''
    Gets a 'term' from the user and, if the card with the term is in the deck,
    this card is removed. Otherwise, NoSuchCardError is raised.
    '''
    print("Which card?")
    try:
        term = input()
        if deck.has_term(term):
            deck.remove_card(term)
        else:
            raise NoSuchCardError
    except NoSuchCardError:
        print(f'Can\'t remove "{term}": there is no such card.\n')


def import_file(deck: Deck, file_name=None) -> None:
    '''
    Accepts filename from user and imports the entries as flashcards
    to the deck.
    '''

    try:
        if not file_name:
            print('File name: ')
            file_name = input()
        row = 0
        with open(file_name, 'r') as f_in:
            for line in f_in.readlines():
                card = line.split(":")
                deck.add_card(Card(card[0], card[1], int(card[2].strip())))
                row += 1
            print(f'{row} cards have been loaded.\n')

    except FileNotFoundError:
        print('File not found.\n')


def export_file(deck: Deck, file_name=None) -> None:
    '''
    Given a filename from the user, export the deck to the given file.
    '''

    try:
        if not file_name:
            print('File name: ')
            file_name = input()
        with open(file_name, 'w+') as f_out:
            for card in deck.cards:
                f_out.write(f'{card.term}:{card.definition}:{card.mistakes}\n')
        print(f'{deck.size()} cards have been saved.\n')
        deck.clear()
    except FileNotFoundError:
        print('Failed.')


def ask(deck: Deck) -> None:
    '''
    Recieves integer input from user of how many times to ask, then
    runs the card_practice function with the user.
    '''
    print('How many times to ask?')
    while True:
        try:
            times_ask = int(input())
            break
        except ValueError:
            print('Please enter an integer!')
    card_practice(deck, times_ask)


def card_practice(deck: Deck, times: int) -> None:
    '''
    Given a deck and number of times to 'ask', this function
    cycles through cards in the deck for the user to practice on.
    '''
    count = 0
    while count < times:
        for card in deck.cards:
            if count == times:
                break
            print(f'Print the definition of "{card.term}": ')
            answer = input()
            if answer == card.definition:
                print('Correct!')

            elif answer in deck.definitions():
                term = deck.get_term(answer)
                print(f'Wrong. The right answer is "{card.definition}", but your definition is correct for "{term}".')
                card.add_mistake()

            else:
                print(f'Wrong. The right answer is "{card.definition}". ')
                card.add_mistake()

            count += 1


def log() -> None:
    '''
    Gets a filename from the user to log forward progress (i/o) and writes
    to the given file.
    '''
    print('File name:')
    file_name = input()
    os.rename('/Users/warrencrutcher/PycharmProjects/pythoncore/Flashcards/Flashcards/task/default.txt', f'/Users/warrencrutcher/PycharmProjects/pythoncore/Flashcards/Flashcards/task/{file_name}' )
    print('The log has been saved.')


def hardest_card(deck: Deck) -> None:
    cards = deck.hardest_card()
    print(len(cards))
    if not cards:
        print('There are no cards with errors.')
    elif len(cards) == 1:
        card = cards[0]
        print(f'The hardest card is "{card.term}". You have {card.mistakes} errors answering it.')
    else:
        hardest = [x.term for x in cards]
        print(f'The hardest cards are ({hardest}). You have {cards[0].mistakes} errors answering them.')


def reset(deck: Deck) -> None:
    for card in deck.cards:
        card.reset()
    print('Card statistics have been reset.')



def main() -> None:
    sys.stdin = LoggerIn('default.txt')
    sys.stdout = LoggerOut('default.txt')
    deck = Deck()
    parser = argparse.ArgumentParser(description='Process Import and Export commands from terminal.')
    parser.add_argument('--import_from', type=str)
    parser.add_argument('--export_to', type=str)
    args = parser.parse_args()
    inputs = [k for k in vars(args) if getattr(args, k)]
    if inputs:
        if 'import_from' in inputs:
            import_file(deck, args.import_from)

    while True:
        command = menu()
        if command == 'exit':
            if not inputs:
                print('Bye bye!')
            elif 'export_to' in inputs:
                export_file(deck, args.export_to)

            break
        if command == 'add':
            add(deck)
        if command == 'remove':
            remove(deck)
        if command == 'import':
            import_file(deck)
        if command == 'export':
            export_file(deck)
        if command == 'ask':
            ask(deck)
        if command == 'log':
            log()
        if command == 'hardest card':
            hardest_card(deck)
        if command == 'reset stats':
            reset(deck)

if __name__ == '__main__':
    main()
