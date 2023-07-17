# Welcome to Multi-Functional-Bot 👋

[![Python application](https://github.com/Naviamold1/Multi-Functional-Discord-Bot/actions/workflows/python-app.yml/badge.svg)](https://github.com/Naviamold1/Multi-Functional-Discord-Bot/actions/workflows/python-app.yml)
[![Docker Image CI](https://github.com/Naviamold1/Multi-Functional-Discord-Bot/actions/workflows/docker-image.yml/badge.svg)](https://github.com/Naviamold1/Multi-Functional-Discord-Bot/actions/workflows/docker-image.yml)
[![CodeQL](https://github.com/Naviamold1/Multi-Functional-Discord-Bot/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/Naviamold1/Multi-Functional-Discord-Bot/actions/workflows/github-code-scanning/codeql)
[![Black coding style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Twitter: naviamold](https://img.shields.io/twitter/follow/naviamold.svg?style=social)](https://twitter.com/naviamold)

> Bot with variety of function like cooking, geography trivia, url shortening, weather telling and more.

## Install

```sh
git clone https://github.com/Naviamold1/Multi-Functional-Discord-Bot.git
cd Multi-Functional-Discord-Bot
cp .env.template .env
```

### ENV File

Open the `.env` file and fill it in with asked values.

Here's a list where you can get each values.

| ENV                | Place to get it from                                          |
| ------------------ | ------------------------------------------------------------- |
| BOT_TOKEN          | <https://discord.com/developers/>                             |
| SPOONACULAR_SECRET | <https://spoonacular.com/food-api>                            |
| CUTTLY_SECRET      | <https://cutt.ly/edit>                                        |
| WEATHER_SECRET     | <https://home.openweathermap.org/api_keys>                    |
| DB_SECRET          | If using Docker leave empty, else any Postgresql Database URI |

### Continue **EITHER** with [Docker Installation](#docker-installation-recommended) **OR** [Manual Installation](#manual-installation)

### [Docker](https://www.docker.com/) Installation (recommended)

If you have already installed [Docker](https://www.docker.com/) on your system just run the following command:

```docker
docker compose up -d
```

---

### Manual Installation

### Continue **EITHER** with [Pip](#using-pip) **OR** [Pipenv](#using-pipenv) to install dependencies

- If you don't know what Pipenv is just go with [Pip](#using-pip)

- If you are planing to contribute to this repo please go with [Pipenv](#using-pipenv)

### Using Pip

```sh
pip install -r requirements.txt
python main.py
```

### Using [Pipenv](https://pipenv.pypa.io/en/latest/installation/#preferred-installation-of-pipenv)

```sh
pipenv shell
pipenv install
pipenv run python main.py
```

## Usage

After running and adding bot to your server simply type `/` to view and use command.

To get a full list of commands you can type `/help` but make sure to select your bots command.

## Author

👤 **Naviamold**

- Twitter: [@naviamold](https://twitter.com/naviamold)
- Github: [@Naviamold1](https://github.com/Naviamold1)

## 🤝 Contributing

Contributions, issues and feature requests are welcome!

Though if you do plan to contribute please install and set this up via [Pipenv](#using-pipenv).

Feel free to check [issues page](https://github.com/Naviamold1/Multi-Functional-Discord-Bot/issues).

## Show your support

Give a ⭐️ if this project helped you!

---

_This README was generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_
