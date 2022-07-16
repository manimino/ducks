from hashindex import HashIndex, get_attributes
from dataclasses import dataclass
from words import all_wordle_words  # contains all 5-letter Wordle words


@dataclass
class Word:
    c0: str
    c1: str
    c2: str
    c3: str
    c4: str

    def __repr__(self):
        return f"{self.c0}{self.c1}{self.c2}{self.c3}{self.c4}"


mi = HashIndex(get_attributes(Word))

for w, _ in all_wordle_words:
    mi.add(Word(w[0], w[1], w[2], w[3], w[4]))
mi.freeze()

# CLEAN got yellow on 'C', green on 'A'.
r = mi.find(
    match={"c3": "A"},
    exclude={
        "c0": list("CLEN"),
        "c1": list("LEN"),
        "c2": list("LEN"),
        "c4": list("LEN"),
    },
)
print(len(r))
# for w in r:
#     print(w)


# SQUAD got green on S and A.
r = mi.find(
    match={"c0": "S", "c3": "A"},
    exclude={"c1": list("LENQD"), "c2": list("LENQD"), "c4": list("LENQD"),},
)
print(len(r))
# for w in r:
#    print(w)


# SCRAM got green on SCRA.
r = mi.find(
    match={"c0": "S", "c1": "C", "c2": "R", "c3": "A"},
    exclude={"c1": list("LENQDM"), "c2": list("LENQDM"), "c4": list("LENQDM"),},
)

print(len(r))
for w in r:
    print(w)
