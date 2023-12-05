# Django Templater

Create Django templates from HTML files

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Django Templater](#django-templater)
  - [Description](#description)
  - [Installation](#installation)
  - [How does it work?](#how-does-it-work)
    - [Convert entire project](#convert-entire-project)
    - [Convert assets URL](#convert-assets-url)
  - [Quick Start](#quick-start)
    - [Convert entire project](#convert-entire-project-1)
    - [Convert assets URL](#convert-assets-url-1)
  - [Advanced Usage](#advanced-usage)
    - [Convert entire project](#convert-entire-project-2)
      - [Static Files](#static-files)
      - [Downloading Remote Files](#downloading-remote-files)
      - [Remote templates](#remote-templates)
    - [Convert assets URL](#convert-assets-url-2)
      - [Static Files](#static-files-1)
      - [Changing output directory](#changing-output-directory)
      - [Downloading Remote Files](#downloading-remote-files-1)
  - [Contributing](#contributing)
  - [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Description

`Django Templater` is a command line tool that will help you to convert your HTML templates to Django templates.

## Installation

```bash
> pip install django-templater
```

## How does it work?

### Convert entire project

This working mode will convert all HTML files in the specified directory to Django templates and split them into master page and child pages

To create a new Django project, you need to specify the main block name. The main block name is the name of the block that will be used in the base HTML file. The main block name is required.

For example:

**Base HTML file**

```html
<!-- ./templates/base.html -->
<html lang="en">
    <head>
        <title>My Website</title>
    </head>
    <body>
        <div class="header" id="main_block">
            <h1>My Website</h1>
            <p>Welcome to my website</p>
        </div>
    </body>
</html>
```

**Home HTML file**

```html
<!-- ./templates/home.html -->
<html lang="en">
    <head>
        <title>My Website</title>
    </head>
    <body>
        <div class="header" id="main_block">
            <h1>User Home</h1>
            <p>Welcome to the user home page</p>
            <img src="assets/images/logo.png" alt="Logo">
        </div>
    </body>
</html>
```

On the above example, the main block name is `main_block`. So, when you create a new Django project, the main block name will be used as the name of the block in the base HTML file.

### Convert assets URL

This working mode will convert all assets URL in the specified directory to Django static URL.

For example:

**Home HTML file**

```html
<!-- ./templates/home.html -->
<html lang="en">
    <head>
        <title>My Website</title>
    </head>
    <body>
        <div class="header" id="main_block">
            <h1>User Home</h1>
            <p>Welcome to the user home page</p>
            <img src="assets/images/logo.png" alt="Logo">
        </div>
    </body>
</html>
```

On the above example, the assets URL is `assets/images/logo.png`. So, when you create a new Django project, the assets URL will be converted to Django static URL:

```html
<html lang="en">
    <head>
        <title>My Website</title>
    </head>
    <body>
        <div class="header" id="main_block">
            <h1>User Home</h1>
            <p>Welcome to the user home page</p>
            <img src="{% static 'assets/images/logo.png' %}" alt="Logo">
        </div>
    </body>
</html>
```

## Quick Start

### Convert entire project

Let say you have an HTML templates in `./templates` directory. 

- Django master page will be: `./templates/base.html`
- Django home page will be: `./templates/home.html`, `./templates/users.html` or `./templates/home/setting.html`
- HTML main block we want to use is: `main_block`

We want to create a Django project in `./myproject` directory and we want to use `./templates` directory as Django templates directory, and the output will be in `./myproject` directory.

```bash
> dt -b main_block ./templates/base.html -o ./myproject ./templates/* 
```

This command will generate the following files:

```Jinja
<!-- ./output/base.html -->
<html lang="en">
    <head>
        <title>My Website</title>
    </head>
    <body>
        <div class="header" id="main_block">
            {% block main_block %}{% endblock %}
        </div>
    </body>
</html>
```

```Jinja
<!-- ./output/home.html -->
{% extends "base.html" %}
{% load static %}
{% block main_block %}
    <h1>User Home</h1>
    <p>Welcome to the user home page</p>
    <img src="{% static 'assets/images/logo.png' %}" alt="Logo">
{% endblock %}
```

### Convert assets URL

Let say you have a HTML template called `./templates/home.html` and you want to convert all assets URL in this file to Django static URL.

```bash
> dtt templates/home.html
```

> Note: If you don't set the output directory, the result will be printed to the console.


## Advanced Usage

### Convert entire project

#### Static Files

By default this project will copy all static files to the Django static directory. The static directory we'll be `static` in your output directory. You can change the static directory by using `-s` or `--static` option.

```bash
> dt -b main_block -m ./templates/base.html -o ./myproject -s assets ./templates/* 
```

#### Downloading Remote Files

You can also download remote assets automatically. If your HTML files contains remote assets, this project will download the remote assets and copy them to the static directory.

```bash
> dt -b main_block -m ./templates/base.html -D -o ./myproject ./templates/*
```

#### Remote templates

You can also use remote templates. This project will download the remote templates and copy them to the templates directory.

```bash
> dt -b main_block -m https://example.com/base.html -o ./myproject ./templates/*
```

### Convert assets URL

#### Static Files

By default this project will copy all static files to the Django static directory. The static directory we'll be `static` in your output directory. You can change the static directory by using `-s` or `--static` option.

```bash
> dtt -s assets templates/home.html
```

#### Changing output directory

You can change the output directory by using `-o` or `--output` option.

```bash
> dtt -o ./myproject templates/home.html
```

> Note: If you don't set the output directory, assets output will be relative to it.

#### Downloading Remote Files

You can also download remote assets automatically. If your HTML files contains remote assets, this project will download the remote assets and copy them to the static directory.

```bash
> dtt -D templates/home.html
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the MIT license.
