#!/usr/bin/env python3

import sys

# finite state machine
class State(object):
    def __str__(self):
        return "State(%s)"%(self.__dict__,)

    def __getattr__(self, attr):
        return None


def do_blockquote(lines):
    block = '\n'.join(lines)
    block = r"""\begin{quote}
%s
\end{quote}
    """ % block
    return block
    
def all_tags(line, name):
    assert name == name.lower(), name
    lc = line.lower()
    begin = "<%s>"%name
    end = "</%s>"%name
    idx = 0
    while 1:
        i0 = lc.find(begin, idx)
        if i0 == -1:
            break
        i2 = lc.find(end, idx)
        if i2 == -1:
            print("warning: %s without %s"%(begin, end))
            break
        assert idx<=i2
        assert i0<i2
        #assert i2 != -1, "%s without %s"%(begin, end)
        i1 = i0 + len(begin)
        i3 = i2 + len(end)
        # ..... <name>********</name>..........
        #       ^     ^       ^      ^
        #       i0    i1      i2     i3
        yield (i0, i1, i2, i3)
        assert i0<i1<i2<i3

        idx = i3

line = "A<sub>5</sub> B<sub>2</sub>"
assert list(all_tags(line, "sub"))==[(1, 6, 7, 13), (15, 20, 21, 27)]

line = "<b>Addendum:</B>"
assert list(all_tags(line, "b"))==[(0, 3, 12, 16)]


def do_tag(line, html_tag, replacer):
    if "<%s>"%html_tag not in line:
        return line
    tail = 0
    result = ""
    for (i0, i1, i2, i3) in all_tags(line, html_tag):
        result += line[tail : i0]
        #result += r"\%s{%s}"%(latex_cmd, line[i1:i2],)
        result += replacer(line[i1:i2])
        tail = i3
    result += line[tail:]
    return result

line = "called E<sub>8</sub>!  E<sub>8</sub> is known"
assert do_tag(line, "sub", lambda s:"_{%s}"%s)=="called E_{8}!  E_{8} is known"

ENTITIES = [
    ("&phi;", r'\phi '), # lowercase greek
    ("&alpha;", r'\alpha '),
    ("&beta;", r'\beta '),
    ("&pi;", r'\pi '),
    ("&rho;", r'\rho '),
    ("&lambda;", r'\lambda '),
    ("&delta;", r'\delta '),
    ("&tau;", r'\tau '),
    ("&mu;", r'\mu '),
    ("&epsilon;", r'\epsilon '),
    ("&eta;", r'\eta '),
    ("&omega;", r'\omega '),
    ("&theta;", r'\theta '),
    ("&psi;", r'\psi '),
    ("&gamma;", r'\gamma '),
    ("&sigma;", r'\sigma '),
    ("&nu;", r'\nu '),
    ("&zeta;", r'\zeta '),
    ("&Gamma;", r'\Gamma '), # upercase greek
    ("&Alpha;", r'\Alpha '),
    ("&Beta;", r'\Beta '),
    ("&Pi;", r'\Pi '),
    ("&Rho;", r'\Rho '),
    ("&Lambda;", r'\Lambda '),
    ("&Phi;", r'\Phi '),
    ("&Delta;", r'\Delta '),
    ("&Tau;", r'\Tau '),
    ("&Mu;", r'\Mu '),
    ("&Epsilon;", r'\Epsilon '),
    ("&Eta;", r'\Eta '),
    ("&Omega;", r'\Omega '),
    ("&Theta;", r'\Theta '),
    ("&Psi;", r'\Psi '),
    ("&Sigma;", r'\Sigma '),
    ("&rarr;", r'\to '), # symbols
    ("&cong;", r'\cong '), # symbols
    ("&cup;", r'\cup '), # symbols
    ("&cap;", r'\cap '), # symbols
    ("&sum;", r'\sum'),
    ("&prime;", r"'"),
    ("&infin;", r'\infty '),
    ("&frac12;", r'\frac{1}{2} '),
    ("&otimes;", r'\otimes '),
    ("&times;", r'\times '),
    ("&oplus;", r'\oplus '),
    ("&#8224;", r'\dagger '),
    ("&dagger;", r'\dagger '),
    ("&#295;", r'\hbar '),
    ("&lt;", '<'),
    ("&gt;", '>'),
    ("&ge;", r'\ge '),
    ("&le;", r'\le '),
    ("&radic;", r'\sqrt '),
    ("&quot;", '"'),
    ("&amp;", r'\text{\&} '),
    ("&nbsp;", r' '), # meh
]
REWRITES = [
    ("<P>", "\n"),
    ("<BLOCKQUOTE>", r"\begin{quote}"),
    ("</BLOCKQUOTE>", r"\end{quote}"),
    ("<HR>", r"\par\noindent\rule{\textwidth}{0.4pt}")
]
def do_line(line, is_math=False):
    lc = line.lower()
    lc = lc.strip()

    for (k,v) in ENTITIES:
        if "&" not in line:
            break
        line = line.replace(k, v)
    for (k,v) in REWRITES:
        line = line.replace(k, v)
        line = line.replace(k.lower(), v)

    try:
        # send <em>foo</em> to \emph{foo}, etc.
        line = do_tag(line, "em", lambda s:r"\emph{%s}"%s)
        line = do_tag(line, "i", lambda s:r"\emph{%s}"%s)
        line = do_tag(line, "b", lambda s:r"\textbf{%s}"%s)
        line = do_tag(line, "sub", lambda s:r"_{%s}"%s)
        line = do_tag(line, "sup", lambda s:r"^{%s}"%s)
    except:
        print("warning: do_tag failed on line %d in %s" % (state.lno+1, state.name))

    #assert "&" not in line, repr(line)
    if "{&}" in line:
        pass
    elif "&" in line:
        print("warning: html entity in %r"%line)

    return line


def do_verbatim(lines):
    lines = [do_line(line, is_math=True) for line in lines]
    block = '\n'.join(lines)
    block = r"""\begin{verbatim}
%s
\end{verbatim}
    """ % block
    return block

def do_math(lines):
    lines = [do_line(line, is_math=True) for line in lines]
    block = '\n'.join(lines)
    block = r"""$$
%s
$$
    """ % block
    return block
    
def do_pre(lines):
    is_math = False
    block = "\n".join(lines)
    if "<sup>" in block:
        is_math = True
    elif "<sub>" in block:
        is_math = True
    for (k,v) in ENTITIES:
        if k in block:
            is_math = True
            break
    if len(lines) > 3:
        is_math = False
    if is_math:
        block = do_math(lines)
    else:
        block = do_verbatim(lines)
    return block

def do_header(line):
    # hack this...
    line = line.strip()
    line = line.replace("</TABLE>", "")
    result = None
    if "Baez" in line:
        pass
    elif line.startswith("<H4>") and line.endswith("</H4>"):
        line = line[4:-5]
        line = line.strip()
        result = r"\week{%s}"%line
    return result


def do_blocks(state, line):
    lc = line.lower()
    lc = lc.strip()

    #if lc.startswith("<P> "):
    #    line = line[len("<P> "):] # strip this guy off...

    result = None
    if lc == "<p>":
        pass # eat it

    elif lc.startswith("<title>"):
        pass # eat it

    elif lc.startswith("<a name"): 
        result = "% " + line

    elif lc.startswith("</a>"): 
        result = "% " + line

    elif lc == "<pre>":
        assert state.lines is None, state
        state.pre = True
        state.lines = []
    elif lc == "</pre>":
        state.pre = False
        result = do_pre(state.lines)
        state.lines = None
    elif state.pre:
        state.lines.append(line)

#    elif lc == "<blockquote>":
#        assert state.lines is None, state
#        state.blockquote = True
#        state.lines = []
#    elif lc == "</blockquote>":
#        state.blockquote = False
#        result = do_blockquote(state.lines)
#        state.lines = None
#    elif state.blockquote:
#        state.lines.append(line)

    elif lc == "<!-- begin header -->":
        state.header = True
    elif lc == "<!-- end header -->":
        state.header = False
        state.body = True
    elif state.header:
        result = do_header(line)

    elif lc == "<!-- begin footer -->":
        state.footer = True
        state.body = False
    elif lc == "<!-- end footer -->":
        state.footer = False
    elif state.footer:
        pass # eat it

    else:
        result = do_line(line)

    return result


def split_line(line):
    tag = "<PRE>"
    if tag in line:
        items = line.split(tag)
        assert len(items) > 1
        for item in items[:-1]:
            yield item
            yield tag
        yield items[-1]
    else:
        yield line


def process(state, src):

    state.lno = 0

    while state.lno < len(src):

        line = src[state.lno]

        for subline in split_line(line):
            result = do_blocks(state, subline)
            if result is not None:
                yield result
        state.prev = line
        state.lno += 1


def do_html(name, output):

    global state

    state = State()
    state.name = name
    state.header = False
    state.footer = False
    state.body = False

    src = open(name).read()
    src = src.split("\n")
    tgt = []

    failed = False
    try:
        for line in process(state, src):
            tgt.append(line)
    except:
        print("\n\n")
        print("="*79)
        print("parse failed on line %d in %s"%(state.lno+1, name))
        failed = True
        raise

    finally:
    
        if failed:
            tgt.append("\n\n%% parser failed at source line %d"%(state.lno+1))
        #for line in lines:
        #    print(line)
        tgt = '\n'.join(tgt)
        #print(tgt)
        #print(state)
        assert output.endswith(".tex")
        f = open(output, "w")
        print(tgt, file=f)
        f.close()



if __name__ == "__main__":
    name = sys.argv[1]
    output = sys.argv[2]

    do_html(name, output)



