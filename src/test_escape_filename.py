from escape_filenames import escape_filename, unescape_filename

assert escape_filename("normal.txt") == "normal.txt"
assert escape_filename("Xv6 System Call Statistics.latex") == "Xv6 System Call Statistics.latex"
assert escape_filename("Xv6 System Call Statistics.pdf") == "Xv6 System Call Statistics.pdf"
assert escape_filename("scstats-dump.tgz") == "scstats-dump.tgz"
assert escape_filename("scstats-screenshot.png") == "scstats-screenshot.png"
assert escape_filename("name-with-back-\\-slash.txt") == "name-with-back-\\\\-slash.txt"
assert escape_filename("name-with-new-\n-line.txt") == "name-with-new-\\n-line.txt"

assert unescape_filename("Xv6 System Call Statistics.latex") == "Xv6 System Call Statistics.latex"
assert unescape_filename("Xv6 System Call Statistics.pdf") == "Xv6 System Call Statistics.pdf"
assert unescape_filename("scstats-dump.tgz") == "scstats-dump.tgz"
assert unescape_filename("scstats-screenshot.png") == "scstats-screenshot.png"
assert unescape_filename("name-with-back-\\\\-slash.txt") == "name-with-back-\\-slash.txt"
assert unescape_filename("name-with-new-\\n-line.txt") == "name-with-new-\n-line.txt"

assert unescape_filename(escape_filename("Xv6 System Call Statistics.latex")) == "Xv6 System Call Statistics.latex"
assert unescape_filename(escape_filename("Xv6 System Call Statistics.pdf")) == "Xv6 System Call Statistics.pdf"
assert unescape_filename(escape_filename("scstats-dump.tgz")) == "scstats-dump.tgz"
assert unescape_filename(escape_filename("scstats-screenshot.png")) == "scstats-screenshot.png"
assert unescape_filename(escape_filename("name-with-back-\\-slash.txt")) == "name-with-back-\\-slash.txt"
assert unescape_filename(escape_filename("name-with-new-\n-line.txt")) == "name-with-new-\n-line.txt"

print("escape_filenames: Successful.")
