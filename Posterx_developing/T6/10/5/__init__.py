# -*- coding: utf-8 -*-
from .TN_XDownload import TN_X_Downloader
from .TN_X import folders, lng

downloader = TN_X_Downloader(folders, lng)
downloader.start()