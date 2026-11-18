"""Terbilang rupiah (bahasa Indonesia) untuk slip gaji.

  terbilang_rupiah(5500681) -> "Lima Juta Lima Ratus Ribu Enam Ratus Delapan Puluh Satu Rupiah"

Didaftarkan sebagai fungsi Jinja (hooks.py: jinja.methods) sehingga bisa dipanggil di Print Format.
"""

_SATUAN = ["", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh", "delapan", "sembilan", "sepuluh", "sebelas"]
_SKALA = [(10**12, "triliun"), (10**9, "miliar"), (10**6, "juta"), (10**3, "ribu")]


def _bilang(n: int) -> str:
	if n < 12:
		return _SATUAN[n]
	if n < 20:
		return _SATUAN[n - 10] + " belas"
	if n < 100:
		sisa = n % 10
		return _SATUAN[n // 10] + " puluh" + (" " + _bilang(sisa) if sisa else "")
	if n < 200:
		return "seratus" + (" " + _bilang(n - 100) if n > 100 else "")
	if n < 1000:
		sisa = n % 100
		return _SATUAN[n // 100] + " ratus" + (" " + _bilang(sisa) if sisa else "")
	if n < 2000:
		return "seribu" + (" " + _bilang(n - 1000) if n > 1000 else "")
	for batas, nama in _SKALA:
		if n >= batas:
			depan, sisa = divmod(n, batas)
			return _bilang(depan) + " " + nama + (" " + _bilang(sisa) if sisa else "")
	return ""


def terbilang(angka) -> str:
	"""Angka bulat (dibulatkan) menjadi kata, huruf awal tiap kata kapital."""
	n = int(round(float(angka or 0)))
	if n == 0:
		return "Nol"
	kata = _bilang(abs(n)).title()
	return ("Minus " + kata) if n < 0 else kata


def terbilang_rupiah(angka) -> str:
	return terbilang(angka) + " Rupiah"
