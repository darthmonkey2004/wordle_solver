# wordle_solver
OS: Ubuntu 20
Wordle Helper (solver): Uses selenium chrome driver and python3 to generate a words list based on live html updates (user
input), then uses regex pattern matching to determine matches. Exits when single match found.

to install, ensure you have Chrome installed and python3-pip, then run install.sh (sudo chmod a+x install.sh; ./install.sh)

Runs in an incognito Chrome tab, limited automated input (clicks) to bypass opening instructions window... but is the only
action taken, primarily using web scraper method to obtain fresh html and live updates.
