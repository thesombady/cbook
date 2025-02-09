#!/usr/local/bin/python3
import os
import sys
import subprocess
from enum import Enum, IntEnum
from typing import List, Dict
from dataclasses import dataclass
from datetime import date

BOOKPATH = os.path.join(os.getenv('HOME') ,'.cbook/address.book')
TAB = '\t'


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

   res.append('\n'.join(list(map(lambda x: tab_level * TAB + x, sub_res))))
   tab_level -= 1

   res.append( 'If any additional fields are wanted, please add a dicussion about the feature on Github (https://www.github.com/thesombady/cbook).' )

   print('\n'.join(res))


class Mode(IntEnum):
    fzf      = 0
    list_    = 1
    
class searchType(IntEnum):
    email    = 0
    name     = 1
    number   = 2
    birthday = 3
    full     = 4
    tag      = 5

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
                case '--number':
                    self.result_type = searchType.number
                case '--birthday' | '-b':
                    self.result_type = searchType.birthday
                case '--full' | '-f':
                    self.result_type = searchType.full
                case '--from-name' | '-fn':
                    self.input_type = searchType.name
                case '--from-number':
                    self.input_type = searchType.number
                case '--from-birthday' | '-fb':
                    self.input_type = searchType.birthday
                case '--help' | '-':
                    print_help_info()
                    exit(0)
                case 'list':
                    self.mode = Mode.list_
                case str(x) if '--show' in x:
                    number = arg.split('=')[1]
                    if number == 'all' or number == 'ALL':
                        number = 100 # Probably not more than 100 with the same filter
                    else:
                        number = int(number)
                    self.maxOutput = number
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
    email: str
    birthday: date = None
    number: str    = ''
    tag: Tag       = Tag.none

    def __repr__(self):
        res: str = '{} '.format(self.name)
        if self.tag != Tag.none:
            res += '@{} '.format(self.tag)
        res += '| {} '.format(self.email)
        if self.birthday != None and self.number != '':
            return '{} | {} | {}'.format(res, self.birthday, self.number)
        if self.birthday != None and self.number == '':
            return '{} | {}'.format(res, self.birthday)
        if self.birthday == None and self.number != '':
            return '{} | {}'.format(res, self.number)
        if self.birthday == None and self.number == '':
            return res
        
    @staticmethod
    def fromDict(contact):
        birthday = None
        number   = ''
        tag      = Tag.none
        if contact.get('Birthday'):
            birthday = date.fromisoformat(contact['Birthday'])
        if contact.get('Number'):
            number = contact['Number']
        if contact.get('Tag'):
            tag = Tag.from_string(contact['Tag'])
        return Contact(contact['Name'], contact['Mail'], birthday, number, tag)

    def validate(self, filter: searchType, search_term: str, search_tag: Tag) -> bool:
        search_term = search_term.lower()
        tag_filter = True
        if search_tag != None:
            if self.tag == search_tag:
                tag_filter = True
            else:
                tag_filter = False
        match filter:
            case searchType.name:
                return self.name.lower().__contains__(search_term) and tag_filter
            case searchType.email:
                return self.email.lower().__contains__(search_term) and tag_filter
            case searchType.full:
                return str(self).__contains__(search_term) and tag_filter
            case searchType.birthday:
                return str(self.birthday).__contains__(search_term) and tag_filter
            case searchType.number:
                return self.number.__contains__(search_term) and tag_filter
            case searchType.tag:
                return str(self.tag).lower().__contains__(search_term) and tag_filter

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
            contact[key] = value
        CONTACTS[i + 1] = Contact.fromDict(contact) # i + 1 will be the line number

def logAdressBook():
    res: str = ''
    for d in CONTACTS.values():
        res += str(d) + '\n'
    return res


parseAdressBook(loadAdressBook())

def search_with_fzf():
    try:
        result = subprocess.check_output(f'echo "{logAdressBook()}" | fzf', shell=True, text=True).strip()
        line_number = int(subprocess.check_output(f'echo "{logAdressBook()})" | grep -n "{result.split('|')[0]}" ', shell=True, text=True).strip().split(':')[0])
        return result, line_number
    except subprocess.CalledProcessError:
        return None, None  # Handles cases where no selection is made



if __name__ == '__main__':
    pref: Preference = Preference(sys.argv[1:])

    if pref.mode == Mode.fzf:
        selected_contact, number = search_with_fzf()
        if selected_contact == None:
            exit(0)

        match pref.result_type:
            case searchType.email:
                print(CONTACTS[number].email)
            case searchType.name:
                print(CONTACTS[number].name)
            case searchType.number:
                print(CONTACTS[number].number)
            case searchType.birthday:
                print(CONTACTS[number].birthday)
            case searchType.full:
                print(CONTACTS[number])

    elif pref.mode == Mode.list_:
        searchResult: List[Contact] = []
        search_str = (' ').join(pref.arguments).lower()
        if search_str == '':
            print("No input!", file = sys.stderr)
            exit(1)
            
        for contact in CONTACTS.values():
            if contact.validate(pref.input_type, search_str, pref.search_tag):
                searchResult.append(contact)
        if len(searchResult) == 0:
            print("No matches found!", file = sys.stderr)
            exit(1)
        match pref.result_type:
            case searchType.email:
                print(('\n').join(map(lambda x : x.email, searchResult[0:pref.maxOutput])))
            case searchType.number:
                print(('\n').join(map(lambda x : x.number, searchResult[0:pref.maxOutput])))
            case searchType.name:
                print(('\n').join(map(lambda x : x.name, searchResult[0:pref.maxOutput])))
            case searchType.tag:
                print(('\n').join(map(lambda x : x.tag, searchResult[0:pref.maxOutput])))
            case searchType.birthday:
                print(('\n').join(map(lambda x : str(x.birthday), searchResult[0:pref.maxOutput])))


