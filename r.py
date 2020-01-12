import unicodedata

u = '🙏🙏🙏hand'+chr(129321)
print(u)



for i, c in enumerate(u):
    print(i, '%04x' % ord(c), unicodedata.category(c), end=" ")
    print(unicodedata.name(c))

# Get numeric value of second character
#print(unicodedata.numeric(u[1]))