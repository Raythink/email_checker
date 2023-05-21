import re
import dns.resolver
import smtplib


# 正则表达式检查邮件地址格式
class EmailTool():
    MX_DNS_CACHE = {}
    MAIL_FROM = 'hr@51job.com'

    def check_format(self, email):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return False
        return True

    def get_mx_record(self, hostname):
        if hostname not in self.MX_DNS_CACHE:
            # print(f"start to resolve:{hostname}")
            try:
                answers = dns.resolver.resolve(hostname, "MX")
                self.MX_DNS_CACHE[hostname] = []
                for rdata in answers:
                    tu1 = rdata.exchange.labels
                    s1 = ''
                    for idx, by in enumerate(tu1):
                        s1 = s1 + '.' + by.decode()
                    self.MX_DNS_CACHE[hostname].append(s1[1:-1])
            # except dns.resolver.NXDOMAIN:
            #     MX_DNS_CACHE[hostname] = None
            #     print(f"MX not found:{hostname}")
            # except dns.resolver.NoAnswer:
            #     MX_DNS_CACHE[hostname] = None
            #     print(f"DNS NoAnswer:{hostname}")
            # except dns.resolver.LifetimeTimeout:
            #     MX_DNS_CACHE[hostname] = None
            #     print(f"DNS LifetimeTimeout:{hostname}")
            except Exception as e:
                self.MX_DNS_CACHE[hostname] = None
                print(f"Err{type(e).__name__}:{hostname}")
                raise e
        # print(MX_DNS_CACHE[hostname])
        return self.MX_DNS_CACHE[hostname]

    # DNS解析检查邮件地址域名

    def check_domain(self, email):
        domain = email.split('@')[1]
        try:
            # records = dns.resolver.query(domain, 'MX')
            # mx_record = records[0].exchange.to_text().rstrip('.')
            mx_record = ''
            mx_record_list = self.get_mx_record(domain)
            if mx_record_list is None:
                return -2, f'{domain}:域名无MX记录'
            mx_record = mx_record_list[0]

            server = smtplib.SMTP()
            server.set_debuglevel(0)
            server.connect(mx_record)
            server.helo(server.local_hostname)
            server.mail(self.MAIL_FROM)
            code, message = server.rcpt(str(email))
            server.quit()

            return code, message

        except Exception as e:
            return -10, f"{domain}:{type(e).__name__}"

    # 调用上述两个函数检查邮件地址有效性

    def check_validity(self, email):
        code = -1
        msg = ''
        if not self.check_format(email):
            code = -1
            msg = f'{email}:邮件地址格式错误'
        else:
            code, msg = self.check_domain(email)

        return code, msg
