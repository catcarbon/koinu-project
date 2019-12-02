# Koinu Project

## Dev environment setup
### Clone repository
`git clone git@github.com:catcarbon/koinu-project.git && cd koinu-project`

### Create virtualenv and activate
i.e. run `python3 -m venv venv && source venv/bin/activate`

### Install required dependencies
i.e. run `pip install -r requirements.txt`

### Start local mysql server
i.e. `brew install percona-server`
follow steps to setup root password for server and secure installation

### Run development server locally
execute `run.sh` script

The development server will be running on `http://127.0.0.1:5000`

## Running with Nginx (reverse proxy)
