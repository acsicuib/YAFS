from problog.program import PrologString
from problog.core import ProbLog
from problog import get_evaluatable

p = PrologString("""
coin(c1). coin(c2).
0.4::heads(C); 0.6::tails(C) :- coin(C).
win :- heads(C).
evidence(heads(c1), false).
query(win).
""")

get_evaluatable().create_from(p).evaluate()