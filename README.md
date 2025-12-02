# Django 5 Blog Application

A concise guide and README for the **Blog Application** built in the first project of **Django 5 By Example**.

This README helps you structure, run, and understand the core components of the blog app.

---

## 📌 Project Overview

The Blog app is a simple content-publishing system that supports:

* Creating and managing posts
* Using slugs for SEO-friendly URLs
* Tagging posts
* Showing similar posts
* Creating custom model managers
* Adding canonical URLs
* Pagination

---

## 🚀 Features

* Post model containing title, slug, author, body, publish date, status
* Custom model manager (`PublishedManager`) to retrieve published posts only
* Class-based or function-based views for listing and detail pages
* URL routing with slugs and dates
* Templates for rendering lists and details
* Tag filtering using **django-taggit**
* Post sharing via email
* Pagination for post lists

---

## 🛠️ Project Setup

### 1. Create Project & App

```bash
django-admin startproject mysite
cd mysite
python manage.py startapp blog
```

### 2. Add `blog` to Installed Apps

```python
INSTALLED_APPS = [
    ...
    'blog.apps.BlogConfig',
    'taggit',
]
```

---

## 🏁 Running the Project

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Visit:

```
http://127.0.0.1:8000/blog/
```

---

## ✔️ Next Steps

* Add comment system
* Add feeds
* Implement full-text search
* Add sitemap

---

## 📚 Reference

Based on **Django 5 By Example – Project 1 (Blog Application)**.
