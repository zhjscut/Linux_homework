from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib


def _format_addr(s):
    name, addr = parseaddr(s) #按照邮件命名格式：用户名<邮箱地址>，将输入的字符串拆分成用户名和地址
    return formataddr((Header(name, 'utf-8').encode(), addr))

def send_email(message, to_addr, from_addr='403618577@qq.com', password='aswronlivdnibhig', smtp_server='smtp.qq.com'):
    '''发送邮件
        input: 
            message: 要发送的消息内容,str类型
            to_addr：收件人地址，列表类型，元素为str类型，可群发，每个收件人为一个列表元素
            from_addr：发件人地址，str类型
            password：密码，QQ邮箱使用的不是QQ密码，而是授权码
            smtp_server：smtp服务器地址
        output: 无
    '''
    msg = MIMEText(message, 'plain', 'utf-8')
    msg['From'] = _format_addr('Python爱好者 <%s>' % from_addr)
    msg['To']  = ''
    for i in range(0, len(to_addr)):
        msg['To'] += _format_addr('管理员 <%s>' % to_addr[i]) + ';' 
    msg['Subject'] = Header('轻风聊天室', 'utf-8').encode()

    server = smtplib.SMTP_SSL(smtp_server, 465) # SMTP协议默认端口是25，SMTP_SSL协议默认端口是465，现在QQ邮箱不支持SMTP只支持SMTP_SSL
    server.set_debuglevel(0) #如果设置为1，就可以打印出和SMTP服务器交互的所有信息
    server.login(from_addr, password)
    server.sendmail(from_addr, to_addr, msg.as_string()) #to_addr应为list类型，如果是单个字符串可以在外面套个[]
    server.quit()
