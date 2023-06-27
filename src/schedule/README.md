# scheduler

This is a scheduler based on the project [schedule](https://github.com/dbader/schedule) with significant changes, including:

- More flexible in scheduling, based in json;
- Capable of recover when the program is restarted or the system is rebooted;
- More robust in error handling.

## Installation

```bash

```

## Configuration


> You only need to configure PostgreSQL if you want to recover the tasks when the system/program starts.

**You can skip this step if will not intend use recovery resource.**

In order to retrieve the tasks scheduled when the program/system is off, the scheduler needs to connect to a PostgreSQL database. 

> We cannot use SQLite because it does not support some data types that we need.

If you do not have a PostgreSQL database, you can install it by following the instructions [here](https://www.postgresql.org/download/).

Or you can use the docker image. If you have docker installed, you can pull the image by running:

```bash

docker pull postgres

```

Then you can run the image by running:

```bash
docker run --name postgres-sched -e POSTGRES_USER=sched_user -e POSTGRES_PASSWORD=sched_password -e POSTGRES_DB=sched_db -p 5432:5432 -d postgres
```

This will create a container named `postgres-sched` with a database named `sched_db` and a user named `sched_user` with password `sched_password`. The container will be listening on port `5432` on your host machine.

## Usage

> If you want to recover the tasks, you need to configure the database connection (see Configuration section).

Is needed to create an instance of Scheduler, with the **optional** parameter `persist_tasks`. Set to `True` if you want to recover the tasks when the program/system is restarted.

Moreover, if `persist_tasks` is set to `True`, is needed set the following parameters according with your database configuration:

- db_host: The host of the database. Default: localhost;
- db_port: The port of the database. Default: 5432;
- db_name: The name of the database. Default: sched_db;
- db_user: The user of the database. Default: sched_user;
- db_password: The password of the database. Default: sched_password;

### Setting a schedule

The configuration of a schedule must be defined in a json, with the following attributes:
- `start_date` [required]: The date when the schedule will start. Valid formats are:
    - `%Y-%m-%d %H:%M:%S`,
    - `%d-%m-%Y %H:%M:%S`,
    - `%Y-%m-%d %H:%M`,
    - `%d-%m-%Y %H:%M`,
    - `%Y-%m-%d`,
    - `%d-%m-%Y`,
- `timezone` [required]: The timezone of the schedule. Valid timezones are all timezones supported by [pytz](https://pypi.org/project/pytz/);
- `repeat_mode`: The repeat mode of the schedule. Valid modes are:
    - `no_repeat`: The schedule will run only once;
    - `minutely`: The schedule will run every minute;
    - `hourly`: The schedule will run every hour;
    - `daily`: The schedule will run every day at the time defined in `start_date`;
    - `weekly`: The schedule will run every week at the time defined in `start_date`;
    - `monthly`: The schedule will run every month at the time defined in `start_date`;
    - `yearly`: The schedule will run every year at the time defined in `start_date`;
    
