import argparse
import pyotp
import robin_stocks.robinhood as r


def rh_login_before():
    totp  = pyotp.TOTP("My2factorAppHere").now()
    print("Current OTP:", totp)
    login = r.login('','', mfa_code=totp, expiresIn=86400)

def rh_login_after():
    r.login('','',expiresIn=86400)


if __name__ == "__main__":
    stock = 'AAPL'

    # log into Robinhood so you can use the API to get fundamental data
    rh_login_before()