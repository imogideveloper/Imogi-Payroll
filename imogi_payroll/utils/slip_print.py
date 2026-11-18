"""Pembantu Print Format slip gaji.

wkhtmltopdf membuka alamat gambar relatif (/files/...) lewat host situs, yang bisa gagal
(HostNotFoundError) bila host itu tidak dikenali server. Logo karena itu ditanam sebagai data URI.
"""

import base64
import mimetypes
import os

import frappe


def file_data_uri(file_url: str) -> str:
	"""Isi berkas publik (/files/...) sebagai data URI; string kosong bila tidak ada."""
	if not file_url or not file_url.startswith("/files/"):
		return ""
	path = frappe.get_site_path("public", file_url.lstrip("/"))
	if not os.path.isfile(path):
		return ""
	mime = mimetypes.guess_type(path)[0] or "image/png"
	with open(path, "rb") as f:
		return f"data:{mime};base64," + base64.b64encode(f.read()).decode()
