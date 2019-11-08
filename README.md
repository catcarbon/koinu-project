# Koinu Project

## Dev environment setup
### Clone repository
`git clone git@github.com:catcarbon/koinu-project.git && cd koinu-project`

### Create virtualenv and activate
i.e. run `python3 -m venv venv && source venv/bin/activate`

### Install required dependencies
i.e. run `pip install -r requirements.txt`

### Run development server locally
First, export environment variable, i.e. `export FLASK_APP=hello.py`
<br>
&nbsp;&nbsp;&nbsp;&nbsp;... for Windows with Powershell: `$env:FLASK_APP = "hello.py"`
<br>
Then execute `flask run` 
<br>
&nbsp;&nbsp;&nbsp;&nbsp;... or alternatively, just use `python -m flask`

The development server will be running on `https://127.0.0.1:5000`

## Running with Nginx (reverse proxy)
