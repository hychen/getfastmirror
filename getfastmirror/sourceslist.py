def make_debentry(url, code, cat=[], comment=None, disable=False):
    catstr = ' '.join(cat)
    h = ''
    if disable:
        h = '#'
    tpl = [
        '%sdeb %s %s %s' % (h, url, code, catstr),
        '%sdeb-src %s %s %s' % (h,url, code, catstr)
    ]
    if comment:
        tpl.insert(0, comment)
    return '\n'.join(tpl)

class APTsource(object):

    def __init__(self, code):
        self.contents = []
        self.code = code
        self.footer = [
            make_debentry('http://archive.canonical.com/ubuntu',
                           code,
                           ['partner'],
                           """## Uncomment the following two lines to add software from Canonical's
## 'partner' repository.
## This software is not part of Ubuntu, but is offered by Canonical and the
## respective vendors as a service to Ubuntu users.""", disable=True),
            '',
            make_debentry('http://security.ubuntu.com/ubuntu',
                           code,
                           ['main', 'restricted']),
            make_debentry('http://security.ubuntu.com/ubuntu',
                            code,
                            ['universe']),
            make_debentry('http://security.ubuntu.com/ubuntu',
                            code,
                            ['multiverse'])
        ]

    def set_fasturl(self, url):
        self.fasturl = url

    def __repr__(self):
        return self._genstr()

    def _genstr(self):
        self.gen_content(self.fasturl, self.code)
        self.contents.extend(self.footer)
        return '\n'.join(self.contents)

    def gen_content(self, url, code):
        f=self.contents.append
        f(make_debentry(url,
                        code,
                        ['main', 'restricted']))
        f('')
        f(make_debentry(url,
                        code+'-updates',
                        ['main', 'restricted'],
                        """## Major bug fix updates produced after the final release of the
## distribution."""))
        f('')
        f(make_debentry(url,
                        code+'updates',
                        ['universe'],
                        """## N.B. software from this repository is ENTIRELY UNSUPPORTED by the Ubuntu
## team. Also, please note that software in universe WILL NOT receive any
## review or updates from the Ubuntu security team."""))
        f('')
        f(make_debentry(url,
                        code+'updates',
                        ['multiverse'],
                        """## N.B. software from this repository is ENTIRELY UNSUPPORTED by the Ubuntu.
## team, and may not be under a free licence. Please satisfy yourself as to.
## your rights to use the software. Also, please note that software in.
## multiverse WILL NOT receive any review or updates from the Ubuntu
## security team."""))
        f('')
        f(make_debentry(url,
                        code+'-backports',
                        ['main', 'restricted', 'universe', 'multiverse'],
                        """## Uncomment the following two lines to add software from the 'backports'
## repository.
## N.B. software from this repository may not have been tested as
## extensively as that contained in the main release, although it includes
## newer versions of some applications which may provide useful features.
## Also, please note that software in backports WILL NOT receive any review
## or updates from the Ubuntu security team.""", disable=True))
        f('')

    def save(self, path):
        with open(path, 'w') as f:
            f.write(self._genstr())

if __name__ == '__main__':
    f = APTsource('lucid')
    f.set_fasturl('http://tw.archive.com.tw')
    print f
