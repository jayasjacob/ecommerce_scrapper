import smtplib


class SendMail:
    def __init__(self, From, Pass):
        self.From = From
        self.Pass = Pass

    def send_mail(self, MailList, url, old_price, price):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(self.From, self.Pass)
        subject = 'price fell down'
        body = 'check out this link ' + url + "\n price:" + str(price.encode('utf-8'))
        msg = f"Subject:{subject}\n\n{body}"
        for TO in MailList:
            server.sendmail(
                self.From,
                TO,
                msg)
        server.close()
        print("sent")
