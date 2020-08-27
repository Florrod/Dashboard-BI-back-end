# Flask Boilerplate for Profesional Development

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/from-referrer/)
<p align="center">
    <a href="https://youtu.be/ORxQ-K3BzQA"><img height="200px" src="https://github.com/4GeeksAcademy/flask-rest-hello/blob/master/docs/assets/how-to.png?raw=true" /></a>
</p>

## Features

- Extensive documentation [here](https://github.com/4GeeksAcademy/flask-rest-hello/tree/master/docs).
- Integrated with Pipenv for package managing.
- Fast deloyment to heroku with `$ pipenv run deploy`.
- Use of `.env` file.
- SQLAlchemy integration for database abstraction.

## Installation (automatic if you are using gitpod)

> Important: The boiplerplate is made for python 3.7 but you can easily change the `python_version` on the Pipfile.

The following steps are automatically runned withing gitpod, if you are doing a local installation you have to do them manually:

```sh
pipenv install;
mysql -u root -e "CREATE DATABASE example";
pipenv run init;
pipenv run migrate;
pipenv run upgrade;
```

## How to Start coding?

There is an example API working with an example database. All your application code should be written inside the `./src/` folder.

- src/main.py (it's where your endpoints should be coded)
- src/models.py (your database tables and serialization logic)
- src/utils.py (some reusable classes and functions)
- src/admin.py (add your models to the admin and manage your data easily)

For a more detailed explanation, look for the tutorial inside the `docs` folder.

## Remember to migrate every time you change your models

You have to migrate and upgrade the migrations for every update you make to your models:
```
$ pipenv run migrate (to make the migrations)
$ pipenv run upgrade  (to update your databse with the migrations)
```


# Manual Installation for Ubuntu & Mac

⚠️ Make sure you have `python 3.6+` and `MySQL` installed on your computer and MySQL is running, then run the following commands:
```sh
$ pipenv install (to install pip packages)
$ pipenv run migrate (to create the database)
$ pipenv run start (to start the flask webserver)
```


## Deploy to Heroku

This template is 100% compatible with Heroku[https://www.heroku.com/], just make sure to understand and execute the following steps:

```sh
// Install heroku
$ npm i heroku -g
// Login to heroku on the command line
$ heroku login -i
// Create an application (if you don't have it already)
$ heroku create <your_application_name>
// Commit and push to heroku (commited your changes)
$ git push heroku master
```
:warning: For a more detailed explanation on working with .env variables or the MySQL database [read the full guide](https://github.com/4GeeksAcademy/flask-rest-hello/blob/master/docs/DEPLOY_YOUR_APP.md).

Para top productos por plataforma
select line_item.product_name, `order`.platform_id,line_item.quantity from line_item, `order` where line_item.order_id = `order`.id and `order`.platform_id = 1 order by line_item.quantity desc limit 5;

Para top productos por plataforma con product_name
select line_item.product_name
from line_item, `order`,platform 
where `order`.platform_id = platform.id 
and line_item.order_id = `order`.id 
and `order`.platform_id = 1 
group by product_name
order by sum(line_item.quantity) desc limit 5;

Para clientes recurrentes por plataforma 1
select clients.phone, clients.orders_count,`order`.platform_id from clients,`order` where `order`.platform_id = 1 order by clients.orders_count desc limit 5;

select clients.orders_count from clients,`order`, platform where `order`.platform_id = platform.id and clients.orders_count = orders_count and `order`.platform_id = 2 order by clients.orders_count desc limit 5;

select clients.orders_count, clients.phone, clients.customer_id_platform, platform.id from clients,`order`, platform where `order`.platform_id = 2 group by `order`.platform_id order by clients.orders_count desc limit 1;

Para clientes recurrentes por plataforma 2
select clients.customer_id_platform, clients.orders_count,`order`.platform_id from clients,`order` where `order`.platform_id = 2 order by clients.orders_count desc limit 5;

Para ventas totales por plataforma
select round(sum(`order`.total_price)), `order`.platform_id from `order` group by `order`.platform_id;

select line_item.product_name from line_item, `order`,platform where `order`.platform_id = platform.id and line_item.order_id =`order`.id and `order`.platform_id = 1 filter by `order`.date = 365 group by product_name order by sum(line_item.quantity) desc limit 5;


