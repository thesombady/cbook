#!/usr/local/bin/python3
import os
import sys
import subprocess
from enum import Enum, IntEnum
from typing import List, Dict
from dataclasses import dataclass
from datetime import date
import calendar

BOOKPATH = os.path.join(os.getenv('HOME') ,'.cbook/address.book')
TAB = '\t'
ALL = 1000


def print_help_info():
   # Maybe write it in a string instead of this?
   tab_level = 0
   res: List[str] = [tab_level * TAB + 'cbook: a simple, yet effective, addressbook in the terminal']
   sub_res = ['fzf-mode:']
   tab_level += 1
   res.append( tab_level * TAB + '--help: Provde the help menu' )
   sub_res.append( tab_level * TAB + '--name/-n: Output the name' )
   sub_res.append( tab_level * TAB + '--email: Output the email' )
   sub_res.append( tab_level * TAB + '--birthday/-b: Output the birthday' )
   sub_res.append( tab_level * TAB + '--number: Output the number' )

   res.append('\n'.join(list(map(lambda x: tab_level * TAB + x, sub_res))))
   tab_level -= 1
   sub_res = ['list-mode:']
   tab_level += 1
   sub_res.append( tab_level * TAB + '--name: Output the name' )
   sub_res.append( tab_level * TAB + '--email: Output the email' )
   sub_res.append( tab_level * TAB + '--birthday: Output the birthday' )
   sub_res.append( tab_level * TAB + '--number: Output the number' )
   sub_res.append( tab_level * TAB + '--from-name/-fn: Filter by name' )
   sub_res.append( tab_level * TAB + '--from-birthday/-fb: Filter by birthday' )
   sub_res.append( tab_level * TAB + '--from-number: Filter by number' )
   sub_res.append( tab_level * TAB + '--show=(n/ALL): Show n matches, or ALL matches. Defaults to 1' )
   sub_res.append( tab_level * TAB + '--tag=(None/Personal/Work/University): Filter by tag. Previous filters still apply' )
   sub_res.append( tab_level * TAB + '-P/W/U: Filter by tag Personal, Work, and University. Previous filters still apply' )

   res.append('\n'.join(list(map(lambda x: tab_level * TAB + x, sub_res))))
   tab_level -= 1

   res.append( 'If any additional fields are wanted, please add a dicussion about the feature on Github (https://www.github.com/thesombady/cbook).' )

   print('\n'.join(res))


class Mode(IntEnum):
    fzf      = 0
    list_    = 1
    hb       = 2
    
class searchType(IntEnum):
    email    = 0
    name     = 1
    number   = 2
    birthday = 3
    matrix   = 4
    full     = 5
    tag      = 6

class Tag(Enum):
    none       = -1
    Personal   =  0
    Work       =  1
    University =  2

    def __str__(self) -> str:
        if self == self.none:
            return ''
        elif self == self.Personal:
            return 'Personal'
        elif self == self.Work:
            return 'Work'
        elif self == self.University:
            return 'University'

    @staticmethod
    def from_string(tag: str):
        match tag:
            case 'Personal':
                return Tag.Personal
            case 'Work':
                return Tag.Work
            case 'University':
                return Tag.University
            case _:
                return Tag.none

   
class Preference:
    def __init__(self, pref: List[str]):
        self.result_type = searchType.email
        self.input_type  = searchType.name
        self.search_tag  = None
        self.mode = Mode.fzf
        if len(pref) == 0:
            return
        self.arguments: List[str] = []
        self.maxOutput: int = 1
        for arg in pref:
            match arg:
                case '--name' | '-n':
                    self.result_type = searchType.name
                case '--matrix' | '-m':
                    self.result_type = searchType.matrix
                case '--number':
                    self.result_type = searchType.number
                case '--birthday' | '-b':
                    self.result_type = searchType.birthday
                case '--from-email' | '--from-mail':
                    self.input_type = searchType.email
                case '--full' | '-f':
                    self.result_type = searchType.full
                case '--from-name' | '-fn':
                    self.input_type = searchType.name
                case '--from-number':
                    self.input_type = searchType.number
                case '--from-birthday' | '-fb':
                    self.input_type = searchType.birthday
                case 'HAPPYBIRTHDAY' | 'HB':
                    self.mode = Mode.hb
                case '--help' | '-h':
                    print_help_info()
                    exit(0)
                case 'list':
                    self.mode = Mode.list_
                case str(x) if '--show' in x:
                    number = arg.split('=')[1]
                    if number == 'all' or number == 'ALL':
                        number = ALL # Probably not more than 100 with the same filter
                    else:
                        number = int(number)
                    self.maxOutput = number
                case '-P':
                    self.search_tag = Tag.Personal
                case '-W':
                    self.search_tag = Tag.Work
                case '-U':
                    self.search_tag = Tag.University
                case str(x) if '--tag' in x:
                    tag = arg.split('=')[1].lower().capitalize()
                    match tag:
                        case 'Work':
                            self.search_tag = Tag.Work
                        case 'University':
                            self.search_tag = Tag.University
                        case 'Personal':
                            self.search_tag = Tag.Personal
                        case 'None':
                            self.search_tag = Tag.none
                        case _:
                            print('Unknown tag ${tag}', file = sys.stderr)
                            exit(1)
                case _:
                    self.arguments.append(arg)
            if len(self.arguments) > 0 and self.mode == Mode.fzf:
                print("Don't provide arguments for fzf-mode", file = sys.stderr)
                exit(1)

        
@dataclass
class Contact:
    name: str
    mail: str
    birthday: str  = None
    number:   str  = None
    tag:      Tag  = Tag.none
    matrix:   str  = None

    def __str__(self):
        fields: List[str] = [self.name] 
        if self.tag != Tag.none:
            fields.append(f'@{self.tag}')
        fields.append(self.mail)
        if self.birthday != None:
            fields.append(str(self.birthday))
        if self.number != None:
            fields.append(self.number)
        if self.matrix != None:
            fields.append(self.matrix)
        return (' | ').join(fields)
        
    @staticmethod
    def fromDict(contact):
        tag      = Tag.from_string(contact.get('tag', Tag.none));
        contact['tag'] = tag
        return Contact(**contact) # Can it be done this way?

    def validate(self, filter: searchType, search_term: str, search_tag: Tag) -> bool:
        search_term = search_term.lower()
        keyword_match = str(self.log(filter)).lower().__contains__(search_term)
        # print(self.log(filter), search_term)
        tag_match = self.tag == search_tag if search_tag != None else True
        return keyword_match and tag_match

    def log(self, filter: searchType):
        match filter:
            case searchType.name:
                return self.name
            case searchType.email:
                return self.mail
            case searchType.birthday:
                return self.birthday
            case searchType.number:
                return self.number
            case searchType.matrix:
                return self.matrix
            case searchType.full:
                return str(self)
        

CONTACTS: Dict[int, Contact] = dict()

def loadAdressBook():
    with open(BOOKPATH, 'r') as file:
        book_content = file.read()
    return book_content

def parseAdressBook(book_content: str):
    lines: List[str] = list(filter(lambda x: x != '', book_content.replace('\t', "").split('\n')))
    length: int = len(lines)
    i: int = 0
    while i < length:
        if lines[i].startswith('//'): # Line comments
            lines.pop(i)
            i -= 1
            length -= 1
        i += 1
        
    offsets = []
    for index, line in enumerate(lines):
        if line == 'Contact:':
            offsets.append(index)
    offsets.append(len(lines))
    for i in range(0, len(offsets) - 1):
        offset = offsets[i]
        contact = dict()
        for j in range(offset + 1, offsets[i + 1], 2):
            key = lines[j].strip(':')
            value = lines[j + 1]
            contact[key.lower()] = value
        CONTACTS[i + 1] = Contact.fromDict(contact) # i + 1 will be the line number

def logAdressBook():
    res: str = ''
    for d in CONTACTS.values():
        res += str(d) + '\n'
    return res


parseAdressBook(loadAdressBook())

def search_with_fzf():
    try:
        # TODO: -m and iterate over result instead
        result = subprocess.check_output(f'echo "{logAdressBook()}" | fzf --preview=', shell=True, text=True).strip()
        line_number = int(subprocess.check_output(f'echo "{logAdressBook()})" | grep -n "{result}" ', shell=True, text=True).strip().split(':')[0])
        return result, line_number
    except subprocess.CalledProcessError:
        return None, None  # Handles cases where no selection is made

if __name__ == '__main__':
    pref: Preference = Preference(sys.argv[1:])

    if pref.mode == Mode.fzf:
        selected_contact, number = search_with_fzf()
        if selected_contact == None:
            exit(0)

        print(CONTACTS[number].log(pref.result_type))

    elif pref.mode == Mode.hb:
        # pref.result_type = searchType.birthday
        pref.maxOutput = ALL
        searchResult: List[Contact] = []
        # today = date.today()
        today = date.fromisoformat('20250929')
        daysInMonth = calendar.mdays[today.month]
        # today = calendar.
        for contact in CONTACTS.values():
            if contact.birthday != None:
                birthday = date.fromisoformat(contact.birthday)
                diff: int = birthday.day - today.day 
                if today.day == birthday.day and diff == 0:
                    print(f'Happy birthday to {contact.name} whom is turning {today.year - birthday.year} years old.')
                    continue
                
                
                elif diff < 15 and diff > 0  and birthday.month - today.month == 0:
                    print(f'{contact.name} is turning {today.year - birthday.year} years old in {diff} day(s)')
                    continue
                elif diff % daysInMonth < 15 and birthday.month - today.month == 1:
                    print(f'{contact.name} is turning {today.year - birthday.year} years old in {diff % daysInMonth} day(s)')
    elif pref.mode == Mode.list_:
        searchResult: List[Contact] = []
        search_str = (' ').join(pref.arguments).lower()
        if search_str == '' and pref.maxOutput == ALL:
            for contact in CONTACTS.values():
                if contact.validate(pref.input_type, '', pref.search_tag):
                    match = contact.log(pref.result_type)
                    print(match) if match != None else ''
            exit(0)

        if search_str == '':
            print("No input!", file = sys.stderr)
            exit(1)
            
        for contact in CONTACTS.values():
            if contact.validate(pref.input_type, search_str, pref.search_tag):
                searchResult.append(contact)
        if len(searchResult) == 0:
            print("No matches found!", file = sys.stderr)
            exit(1)
        searchResult = searchResult[0:pref.maxOutput]

        print(('\n').join(map(lambda x: x.log(pref.result_type), searchResult)))
