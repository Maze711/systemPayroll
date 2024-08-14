# lib.py

from logging.handlers import RotatingFileHandler
import sys
import os
import mysql.connector
from mysql.connector import Error
import pandas as pd
import logging
import xlrd
from datetime import datetime, timedelta, date
from time import *
import time
from functools import wraps
import traceback
import bcrypt
import openpyxl
from email.message import EmailMessage
import ssl
import smtplib

from dotenv import load_dotenv

from PyQt5.QtCore import QTimer, QDate, Qt, QEvent, QTime, QObject, pyqtSignal, QThread, QRect
from PyQt5.QtGui import QFont, QFontDatabase, QIntValidator, QStandardItemModel, QScreen
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QVBoxLayout, QFileDialog, QMessageBox, QHeaderView,
    QPushButton, QTableWidgetItem, QPlainTextEdit, QComboBox, QDateEdit, QLineEdit,
    QDialog, QProgressBar, QLabel, QWidget, QTableWidget, QCheckBox, QStackedWidget
)
from PyQt5.uic import loadUi

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5 import QtWidgets, QtCore
