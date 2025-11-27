import pyotp
import robin_stocks.robinhood as r
totp  = pyotp.TOTP("My2factorAppHere").now()
login = r.login('adhocsteve@outlook.com','RobinPass99', mfa_code=totp)