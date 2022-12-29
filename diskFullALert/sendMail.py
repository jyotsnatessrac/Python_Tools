import smtplib, ssl, subprocess
from time import sleep
import configparser
import logging
from logging.handlers import RotatingFileHandler

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")

config = configparser.ConfigParser()
config.read_file(open(r'/home/user/Tessrac/PythonScripts/config.ini'))
threshold = config.get('System', 'threshold')
partition = config.get('System', 'partition')
log_file = (config.get('Logger','log_file')).strip('\"')
# partition = '/'

def get_file_handler():

    file_handler = RotatingFileHandler(log_file, mode='a', backupCount=3)
    file_handler.setFormatter(FORMATTER)
    return file_handler

def get_logger(logger_name):
   logger = logging.getLogger(logger_name)
   logger.setLevel(logging.DEBUG) # better to have too much log than not enough
   logger.addHandler(get_file_handler())
   return logger

def sendMail(data):

    port = int(config.get('Mail Server', 'port'))  # For SSL
    smtp_server = (config.get('Mail Server', 'smtp_server')).strip('\"')
    sender_email = (config.get('Mail Server','sender_email')).strip('\"')
    receiver_email = (config.get('Mail Server','receiver_email')).strip('\"')
    password = (config.get('Mail Server','password')).strip('\"')

    subject = 'Disk Space Full Alert for STARC'
    alert_msg = 100 - int(data[4][:-1])
    message = 'Subject:{}\n\nDiskSpace Available: {}%,   DiskSpace Used: {}'.format(subject,alert_msg,data[4])

    context = ssl.create_default_context()
    print(port, smtp_server)
    with smtplib.SMTP_SSL(smtp_server, int(port), context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
        log.info(message)

def check_once():
    df = subprocess.Popen(['df','-h'], stdout=subprocess.PIPE)
    for line in df.stdout:
        splitline = line.decode().split()
        if (splitline[5]) == (partition.strip('\"')):
            if int(splitline[4][:-1]) > int(threshold):
                # log.info(f"Percentage of diskspace: {splitline[4]}")
                sendMail(splitline)

if __name__ == "__main__":
    
    log = get_logger('disk_log')
    
    while True:
        check_once()
        sleep(3600)
