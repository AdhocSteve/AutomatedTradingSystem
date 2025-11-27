import pyotp
import robin_stocks.robinhood as r
totp  = pyotp.TOTP("My2factorAppHere").now()
login = r.login('','', mfa_code=totp)