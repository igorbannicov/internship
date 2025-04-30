from flask import Blueprint, render_template, redirect, url_for, request, flash
from app import db, bcrypt
from app.models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    # Здесь будет логика регистрации, доступная только админам
    return "Register page (admin only)"

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Здесь будет логика входа
    return "Login page"
