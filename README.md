# Transaction Log App

An app that creates and lists transactions given a user.

This app was made using the Django Rest Framework. To run this app you will need:

1. Python 3.8 installed
2. Pip installed
3. Postgres database

On this File you will find:
- Installation
- Installation using Docker
- How to use
- Running Tests
- Improvments (Personal Toughts about the project)

## Installation

After you cloned the repo, or unzipped the project you need to:

### 1 Create a `.env` file

You can simply copy the `.env.example` to a `.env` file and replace the env vars with the appropriate ones with your system:

```sh
cp .env.example .env
```

### 2 Install the project packages

The required packages are described in the `requirements.txt` file. You can install it using pip:

```sh
pip install -r requirements.txt
```

### 3 Database setup

Now we need to set up our database. To do this, first let's create a new DB on Postgres for our application:

```sh
psql -U postgres -c "CREATE DATABASE transactions_db"
```

Make sure to insert the proper user credentials of your postgres environment. With our database created let's create our schema using the `migrate` command:

```sh
python manage.py migrate
```

If everything goes well, you should see the logs of the migrations printed at your screen


### 4 Run the app

After all of this setup it's time to run our app:

```sh
python manage.py runserver
```

And that's it! You can start making requests to your localhost:8000!

### Installation troubleshooting

- The most common case of problem is involving the postgres connection with the database, make sure that you have the proper PG_CONFIG setup in your `.env` files and postgres is ready to take requests.
- Another possible problem is while executing `python` commands. If you have previous versions of Python installed (i.e Python 2.X) maybe you want to replace `python` with `python3`. You can easily check your python version with `python --version`

## Installation using Docker

If you wish to use Docker to run this app, the process is a bit different since the `Dockerfile` handles all the setup of the app.

### Every time
Just run the command to bring the project up:

```sh
docker-compose up -d
```

And if you want to stop and remove the containers:

```sh
docker-compose stop && docker-compose rm -f
```

This should bring every service up and connected with each other. After this you are good to go!

### ON THE FIRST RUN
This steps are required only at the first time that you run the app because we need to make the migrations of the project in order for it to properly function

#### 1 Start only the Postgres and Nginx services
```
docker-compose up -d postgres nginx
```

This will start these two services in the background, they will keep running after that and you can check it by running `docker-compose ps`

#### 2 Run the migrations
```
docker-compose run --rm app python manage.py migrate
```

This command will create a container of our app, run the migration and kill the container, so you don't have to remove it latter

#### 3 Run the app
Now, if everything went well on the last command, you should be able to run the app with:
```sh
docker-compose up -d --build app
```

### Troubleshooting docker installation

- The most common errors are regarding the environment variables defined in the `docker-compose.yml` and `.env.example` if they don't match you will probably be facing some errors of connection between the app and the database, so make sure they have the same value!
- Another possible error is that when the app runs the postgres instance will be initializing so this makes the app throw an error because at the time of checking the database was not available.
  - If this happens, just run `docker-compose restart app` to restart the app service and you should be good to go!

## How to use this app

To use this app you will have to first create a user then authenticate. After doing this two steps you can start to make some requests to the `/transactions` endpoint.

Here is a link for a detailed [API Documentation](https://documenter.getpostman.com/view/2993978/2s93CSoAbY) for each available endpoint. This documentation was built using Postman. In this repo you will also find a complete Postman's collection at the `docs` folder. You can just import the collection to your postman's workspace.

### Create transactions

There are two main ways to create new transactions in the system:

#### Manually making a POST request

You can make a post request to `http://localhost:8000/transactions/`. The body of the request is:
```json
{
    "type": 1,
    "value": 1000,
    "merchant": null
}
```

Transactions type 1 are Deposits, 2 are Withdrawals and 3 is Expenses. To create an `expense` transaction you need to fill the `merchant` property

#### Upload a CSV file

You could also make a POST to `http://localhost:8000/transactions/csv_upload/` passing a `file` parameter with the transactions that you want to load.

Note that this operation will take into account the user balance, and **in any chance that the balance turn negative it will revert all the transactions**!

To see the file schema you can check the `data_samples` folder which contain some example of valid and invalid transactions


## Running tests

Note the tests on this projects are **Integration Tests** so you must have a valid connection to your database in order to run the test suite. All db operations are handled by the `test` command so you don't have to do anything regarding it.

If you install the app locally, you could just run:

```sh
python manage.py test transactions.tests
```

And in docker you can:
```sh
docker-compose run --rm app python manage.py test transactions.tests
```

But make sure that the postgres container is also running!

## Improvement Points & Thoughts on the project

This was the first time that I ever used the Django Framework and I enjoyed the coding! It reminds me of Laravel, especially how opinative the framework is compared to Flask.

My intention with this app was to make it the most simple as possible, and because of this some conventions were left aside in favor of simplicity to read the code itself. This is clear by how my `models` and `views` are organized in the same file, instead of creating a proper namespace for each one, but due to the simplicity of the project I believe that this is a good tradeoff. I understand that in a production system I would have to organize these files and classes in a better way.

Beside the "code allocation" aspect, I could also polish more the response of the API, especially parsing the "hard int" like `type` and `userId`, but I'm not super familiar with the framework and given the limited time frame I opt to focus on the proper working of the app regarding transactions handling.

Finally I also have in mind that I'm perform integrations tests for the system, instead of unit testing it, but since almost all of the code is inside Django's structure (i.e: Views, Models, Serializers) using this type of test is ok because we end up testing the system as a whole.

Overall I really enjoyed building this project and I'm happy with my work. Hope you enjoy it too :)
