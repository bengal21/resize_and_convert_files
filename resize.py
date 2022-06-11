from PIL import Image
import os
import fitz
import email
import imaplib
import smtplib
from email.header import decode_header
from email.message import EmailMessage
import time


while True:
    try:
        time.sleep(5)
        # checking mail and getting files
        imap = imaplib.IMAP4_SSL('imap.mail.ru')
        imap.login('your email', 'login')
        status, mess = imap.select('testbot')
        res, data = imap.uid('search', None, 'UNSEEN')
        raw_mail = int(data[0].split()[-1])
        status1, inf = imap.uid('fetch', str(raw_mail), "(RFC822)")
        get_inf = inf[0][1]
        email_message = email.message_from_bytes(get_inf)
        attach = email_message.get_payload()
        attach_without_0 = attach.pop(0)
        sender, encoding = decode_header(email_message["Return-path"])[0]
        sender_back = sender[:-1][1::]

        # split files to folders
        r = 0
        for file in attach:
            file.get_content_type()
            type_of_file = file.get_content_type().split('/')[1]
            if type_of_file.lower() == 'pdf':
                open(f'/new_env/v_mail_for_resize/pdf/{r}.{type_of_file}', 'wb').write(file.get_payload(decode=True))
                r += 1
            else:
                open(f'/new_env/v_mail_for_resize/png_jpeg/{r}.{type_of_file}', 'wb').write(file.get_payload(decode=True))
                r += 1

        # resize files
        a = 0
        for files in os.listdir('/new_env/v_mail_for_resize/png_jpeg'):
            size_of_file = os.path.getsize(f'/new_env/v_mail_for_resize/png_jpeg/{files}')
            if size_of_file > 1000000:
                image_for_resize = Image.open(f'/new_env/v_mail_for_resize/png_jpeg/{files}')
                image_size = Image.open(f'/new_env/v_mail_for_resize/png_jpeg/{files}').size
                index_of_size = image_size[0] / image_size[1]
                size_of_image = int(1000 / index_of_size)
                resized_image = image_for_resize.resize((1000, size_of_image))
                resized_image.save(f'/new_env/v_mail_for_resize/for_sending/{files}{a}.jpeg')
                a += 1
            else:
                image_for_save = Image.open(f'/new_env/v_mail_for_resize/png_jpeg/{files}')
                image_for_save.save(f'/new_env/v_mail_for_resize/for_sending/{files}{a}.jpeg')
                a += 1

        # split pdf and convert to jpeg
        for file_pdf in os.listdir('/new_env/v_mail_for_resize/pdf'):
            doc = fitz.open(f'/new_env/v_mail_for_resize/pdf/{file_pdf}')
            number_of_pages = doc.page_count
            for i in range(number_of_pages):
                page = doc.load_page(i)
                pix = page.get_pixmap(dpi=130)
                output = f'/new_env/v_mail_for_resize/for_sending/{file_pdf}{i}.jpeg'
                pix.save(output)

        # sending back
        ms = EmailMessage()
        ms['Subject'] = 'Have a good day!)'
        ms['From'] = 'leonov_dubai@mail.ru'
        ms['To'] = sender_back
        ms.set_content(' ')
        server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
        server.login('your email', 'login')
        for i in os.listdir('/new_env/v_mail_for_resize/for_sending'):
            with open(os.path.join('/new_env/v_mail_for_resize/for_sending/', i),'rb') as f:
                file1 = f.read()
                file_name = f.name
                ms.add_attachment(file1, maintype='aplication', subtype='octec-strem', filename=file_name)
        server.send_message(ms)
        server.quit()


        for files1 in os.listdir('/new_env/v_mail_for_resize/png_jpeg'):
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), f'/new_env/v_mail_for_resize/png_jpeg/{files1}')
            os.remove(path)
        for files2 in os.listdir('/new_env/v_mail_for_resize/pdf'):
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), f'/new_env/v_mail_for_resize/pdf/{files2}')
            os.remove(path)
        for files3 in os.listdir('/new_env/v_mail_for_resize/for_sending'):
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), f'/new_env/v_mail_for_resize/for_sending/{files3}')
            os.remove(path)
    except:
        continue