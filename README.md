# inkan-challenge
Josep Sauch Inkan Wargame challenge

## Requirements

### Python

- python >= 3.9(could work with earlier versions, not tested)
- pip >=22.3.1 (could work with earlier versions, not tested)

#### Pip Packages

- Django >= 4.1.0
- Polymorphic Models for Django >=3.1.0

## Installation

In order to install the project locally run the following commands.

### Clone the project

``` git clone https://github.com/JSauch/inkan-challenge/ && cd inkan-challenge```

### (Optional) Create a new virtual enviroment

``` python3 -m venv /path/to/new/virtual/environment ```
``` source /path/to/new/virtual/environment/bin/activate ```

### Install dependencies for python

``` pip install -r requirements.txt ```

### Setup the django app

Run migrations

``` python manage.py migrate ```

Run the tests everything should pass

``` python manage.py test ```

