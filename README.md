# Django Templater

Create Django templates from HTML files

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)

## Description

`Django Templater` is a command line tool that will help you to convert your HTML templates to Django templates.

## Installation

```bash
> pip install django-templater
```

## How does it work?

This project will create a new Django project and copy all HTML files to the Django templates directory. It will also create a new Django app and copy all HTML files to the Django templates directory.

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

## Quick Start

Let say you have an HTML templates in `./templates` directory. 

- Django master page will be: `./templates/base.html`
- Django home page will be: `./templates/home.html`, `./templates/users.html` or `./templates/home/setting.html`
- HTML main block we want to use is: `main_block`

We want to create a Django project in `./myproject` directory and we want to use `./templates` directory as Django templates directory, and the output will be in `./myproject` directory.

```bash
> dt -b main_block ./templates/base.html -t ./templates/* -o ./myproject
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

## Advanced Usage

### Static Files

By default this project will copy all static files to the Django static directory. The static directory we'll be `static` in your output directory. You can change the static directory by using `-s` or `--static` option.

```bash
> dt -b main_block -m ./templates/base.html -o ./myproject -s assets ./templates/* 
```

### Downloading Remote Files

You can also download remote assets automatically. If your HTML files contains remote assets, this project will download the remote assets and copy them to the static directory.

```bash
> dt -b main_block -m ./templates/base.html -D -o ./myproject ./templates/*
```

### Remote templates

You can also use remote templates. This project will download the remote templates and copy them to the templates directory.

```bash
> dt -b main_block -m https://example.com/base.html -o ./myproject ./templates/*
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the MIT license.
