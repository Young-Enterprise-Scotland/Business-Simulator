# Business Simulator

## Setup

### Git/Repo Setup

1. Fork the git repo to your profile.

2. Clone repository.

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

1. Install MySQL on your system.

    `sudo apt-get install mysql-server`

    `sudo apt-get install libmysqlclient-dev`
2. Start MySQL, create new user and make a database.

    `sudo mysql`

    `CREATE USER account_name IDENTIFIED BY 'password';`

    ```GRANT ALL ON `%`.* TO account_name@`%` ```

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
