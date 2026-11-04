import frappe

no_cache = 1

POS_ROUTE = "/app/point-of-sale"


def get_context(context):
	context.csrf_token = frappe.sessions.get_csrf_token()
	# Where to send them once they are in. A cashier's next act is opening the till, and leaving
	# them to find their own way there is a step that exists only because the two were never
	# wired together. Who gets sent is read from the data — does a POS Profile actually list
	# this user — rather than from a list of names kept here, so a cashier added to a profile
	# tomorrow is carried along without touching this file.
	context.after_checkin = POS_ROUTE if works_the_till(frappe.session.user) else ""


def works_the_till(user: str) -> bool:
	if not user or user == "Guest":
		return False
	return bool(frappe.db.exists("POS Profile User", {"user": user, "parenttype": "POS Profile"}))


@frappe.whitelist()
def where_next() -> str:
	"""The same answer, asked at the moment of check-in instead of when the page was built.

	The page carries the destination in `data-after`, which is enough while it is fresh. A tab
	opened before a cashier was added to a POS Profile — or before this existed at all — carries
	an empty one and would simply sit there after checking in, with nothing on screen explaining
	why. Asking again costs one request and removes that silence.
	"""
	return POS_ROUTE if works_the_till(frappe.session.user) else ""
