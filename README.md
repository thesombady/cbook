> This project has moved direction its updated version is `contacts` found [here](https://www.github.com/thesombady/contacts). It is now more in line with the Unix-philosophy.

# cbook
Cbook, pronounised contact book, is a simple, yet effective terminal addressbook. Fetching mail addresses has never been easier. It’s written in Python for adaptability, and flexibility.

## Getting started

Fun that you want to give ’cbook’. Getting is rather simple, start by cloning the repository, and moving into the directory.
```bash 
git clone https://www.github.com/thesombady/cbook
cd cbook
```

To access cbook from everywhere, and make it an executable, run
```bash
bash install.sh
```
It will check for dependencies, and ask before linking.
To run `cbook`, simly write for Unix bases operating systems
```bash
cbook
```
and for Windows
```Powershell
cbook.bat
```


# How does it work?

Cbook has two modes, Fzf mode, and List mode. By default fzf mode is active.

## Fzf mode

Fzf mode is named fzf mode due to it using fzf to fuzzy search for the search field. This includes all the fields for each individual contact. The default output is the corresponding email-address, that is directed to the terminal, via stdout. To get any of the fields, append the searchfilter, ex. `cbook --birthday`, which would output the birthday of the selected contact.

## List mode

List mode instead lets you pass your search term(s) after the command.
`cbook list foo bar`, searches for the name ”foo bar” in the contact list. As per default in the fzf mode, the default output is the correspondig email address.

# Are you tired of having to remember birthdays?

Cbook have the option to include birthdays in the contact book, therefore, it's possible to search the birthday. You can list all upcoming birthdays by just running `cbook HAPPYBIRTHDAY`.



