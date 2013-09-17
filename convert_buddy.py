import json
import sys
import decimal
import itertools

pythoncode = sys.stdin.read()
pstruk = eval(pythoncode, globals(), {"Decimal": decimal.Decimal})

fin = {}

fin["people"] = list(pstruk["userdict"].values())

def old_to_new_user_id(userid):
	#indexes = [i for i,x in enumerate(xs) if x == 'foo']
	return fin["people"].index(pstruk["userdict"][userid])

fin["description"] = "imported ledger"

e = []
counter = itertools.count()
for i in pstruk["expenselist"]:
	obj = {"whoshouldpay": [old_to_new_user_id(x) for x in i["users"]]}
	obj["description"] = "expense {0}".format(next(counter))
	obj["whopaid"] = [{"amount": str(payment["amount"]), "personId": old_to_new_user_id(payment["user"])} for payment in i["payments"]]
	e.append(obj)

fin["expenses"] = e

print(json.dumps(fin))
