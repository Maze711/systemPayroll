# lib.py
import functools
import psutil
import threading
import sys
import os
import os.path
import mysql.connector
import pandas as pd
import logging
import xlrd
import time
import calendar
import operator
import traceback
import bcrypt
import openpyxl
import ssl
import smtplib
import warnings
import re
import requests

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email import encoders
from datetime import datetime, timedelta, date
from time import *
from functools import wraps
from mysql.connector import Error
from css_inline import inline
from email.utils import formataddr
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from PyQt5.uic import loadUi
# from MainFrame.systemFunctions import single_function_logger
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import (QTimer, QDate, Qt, QEvent, QTime, QObject, pyqtSignal, QThread, QRect, pyqtSlot, QByteArray,
                          QBuffer, QIODevice)
from PyQt5.QtGui import QFont, QFontDatabase, QIntValidator, QStandardItemModel, QScreen, QCursor, QPixmap, QImage
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QVBoxLayout, QFileDialog, QMessageBox, QHeaderView,
    QPushButton, QTableWidgetItem, QPlainTextEdit, QComboBox, QDateEdit, QLineEdit,
    QDialog, QProgressBar, QLabel, QWidget, QTableWidget, QCheckBox, QStackedWidget,
    QHBoxLayout, QStyledItemDelegate, QAbstractItemView
)