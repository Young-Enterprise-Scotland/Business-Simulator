# Business Simulator

## Deploy

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Docker

1. Install docker from the [offical website](https://www.docker.com/).
2. Change the end of line sequence of wait-for-mysql.sh from CRLF to LF in your text-editor.
3. Make sure port 3306 is free on your machine. To close a certain port: [windows](https://madvens.wordpress.com/2012/06/02/how-to-free-a-port-on-windows/), [Ubuntu](https://stackoverflow.com/a/30753172)
4. go into the root directory of the project.
5. Run `docker-compose up --build` to build the project.

## Setup

### Git/Repo Setup

1. Fork the git repo to your profile.

2. Clone repository.
    `(https://usernname@stgit.dcs.gla.ac.uk/username/cs33-main.git)`

3. Add upstream to forked repo.

    `git remote add upstream https://stgit.dcs.gla.ac.uk/tp3-2020-CS33/cs33-main.git`

### Environment setup

1. Install virtualenv.

    `pip install virtualenv`
2. Create virtual environment.

    `virtualenv env --python=python3.8`
3. Activate virtual environment.

    `source env/bin/activate`
4. Install requirements

    `python -m pip install -r requirements.txt`

### Django and Database Setup

1. Install MySQL on your system.*

    `sudo apt-get install mysql-server`

    `sudo apt-get install libmysqlclient-dev`
2. Start MySQL, create new user and make a database.

    `sudo mysql`

    `CREATE USER account_name IDENTIFIED BY 'password';`

    ```GRANT ALL ON '%''.* TO 'account_name@'%'' ```

    `exit`
3. Login to your new mysql user.

    `mysql -u account_name -p`

    `CREATE DATABASE BusinessSimulator;`

    `exit`
4. Add `key.py` to the same directory as settings.py

    ```py
    class Key:
        # Secret key to use for django settings
        SECRET_KEY = 'a long string of characters.'
        MYSQL_USERNAME = 'username'
        MYSQL_PASSWORD = 'password'
    ```

## Writing Code

1. Activate virtual environment.

    `source env/bin/activate`
2. On master branch pull changes from upstream.

    `git fetch upstream`
3. Normal Django models stuff.

    `python manage.py makemigrations`

    `python manage.py migrate`

4. Create new branch for feature.

   `git checkout -b new-feature-name`
5. Make changes locally.
6. Commit and push.

    `git add .`

    `git commit -m "Change made to feature"`

    `git push`
7. Visit your repository/branch online and click on 'Create new merge request'.
8. Ask Aaron to review and merge code.


\*If error
```
Package mysql-server is not available, but is referred to by another package.
This may mean that the package is missing, has been obsoleted, or
is only available from another source

E: Package 'mysql-server' has no installation candidate
```
This means that the linux distro requires a slightly different mysql bundle
Follow steps:
1. Remove any current mysql files and upgrade system: 
``` 
sudo apt-get purge mysql-*
sudo apt-get autoremove
sudo apt-get autoclean
sudo apt-get dist-upgrade

sudo rm -rf /etc/mysql
sudo rm -rf /var/lib/mysql*
```
2. Find versions available: `apt-cache search mysql-server`
3. select the mysql-version available. e.g default-mysql-server
4. Install the version available, e.g: `sudo apt-get install default-mysql-server`
5. To get available clients `apt-cache search libmysqlclient-dev`
6. install corresponding client e.g: `sudo apt-get install default-libmysqlclient-dev`
7. Allow non root to run mysql: `sudo chown mysql.mysql /var/run/mysqld/`
8. Finally start the service: `systemctl restart mysql`
9. View `systemctl` and you should see MySql as one of the running processes.  


