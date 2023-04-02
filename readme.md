# Readme.md

## Notes

 - Expected output is ['OK', 'OK', 'OK', 'OK', 'OK', 'failed', 'OK', 'OK', 'skipped'] for end list
 - The program mentions when task is skipped
 - The program **has** to be run in Unix environment, as on Windows it provides the following result :
 - ['failed', 'OK', 'skipped', 'OK', 'OK', 'failed', 'failed', 'OK', 'skipped']

## Installation

 - Unpack secret-interview-test.zip first

###  Type 1 install:

 1. Create a new repository on GitHub with an empty .gitignore file
 2. Drag and drop the all the files within the "secret-interview-test" into WEB UI of GitHub's new repository
 3. Go to GitHub - Actions
 4. Click on "set up a workflow yourself"
 5. Copy-paste the  "main.yml"'s contents that is in "secret-interview-test//.github//workflows" into the text editor in  webUI from your own PC with notepad/alternatives
*Above is done because .github folder is ignored*
6. Verify output after program is ran by clicking on checkmark next to "N commit"
7. There is "Run main file" that runs use case program. Within there are the outputs from during the test run
8. There is "Run pytest file" that tests the code



 - If all above fails, [here](https://github.com/grigsos/secret-interview-test) is the link to what it should look like 
- Let me know if I should remove it/make it hidden for integrity reasons

### Type 2 install:
Ensure you have python 3.8+ installed. Complete below tasks for 
```console
$ curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
$ python get-pip.py
$ pip install -r requirements.txt
$ python main.py
$ python -m pytest

```

 - main file is general execution of program
 - pytest runs unit tests to verify integrity and validity of project
