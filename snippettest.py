from csv import reader
import smtplib


# open csv file and read it line by line
with open('emails.csv', 'r') as f:
    csv_reader = reader(f)
    next(csv_reader)
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("navflag240@gmail.com", 'ilia2019')
    for row in csv_reader:
        msg = f"Dear embassy of {row[1]},\n\n If you choose, you can completely disregard this email. \n I'm a 14-year-old lad from Tbilisi Saburtalo (Georgia), and one of my favorite subjects are geography and history. The reason I'm writing is that I have a small flag collection, but I don't have a flag of {row[1]} which is one of my favorites, so I'd be grateful if you could send me one. \n Best regards, \n Ilia"
        subject = f"Can I ask a favour?"
        body = "Subject: {}\n\n{}".format(subject,msg)
        server.sendmail("navflag240@gmail.com", row , body)
        print(f'{row[0]} sent to {row[1]}')
server.quit()


#
