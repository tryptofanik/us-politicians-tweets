import json
# Opening JSON file
import os
import shutil
import stat

import regex as re


def json_preprocess(path):
    for filename in os.listdir(path):
        if "json" in filename:
            f = os.path.join(path, filename)
            os.chmod(f, stat.S_IRUSR | stat.S_IWUSR)
            f2 = open(f, "r+", encoding="utf-8")
            data = f2.read()

            replaced = re.search(r'(?<={\"body\": \")(.*)(?=\", \"statusCode\")', data)
            if replaced:
                r = replaced.groups()[0]
                new = re.sub(r'(?<={\"body\":)(.*)(?=, \"statusCode\")', r, data)
                new = re.sub(r'(?<=<a href=)(.*)(?=</a>")', "bad input", new)
                new = re.sub(r'[\000-\011\013-\037]', '', new)
                new = new.replace("\\", "")
                new = new.replace("//", "")
                new = re.sub(r'(?<=text\":)(.*)(?=, \"truncated\")', '" "', new)
                new = re.sub(r'(?<=\"description\": )(.*)(?=, \"url\")', '" "', new)
                if new:
                    f2.seek(0)
                    f2.write(new.encode('utf-16', 'surrogatepass').decode('utf-16').encode('utf-8').decode("utf-8"))
                    f2.truncate()
            f2.close()


def test():
    shutil.copyfile(os.path.join('test', 'trial.json'), 'trial.json')
    json_preprocess(r".")
    f3 = open('trial.json', "r+", encoding="utf-8")
    assert json.load(f3, strict=False)
    f3.close()


if __name__ == '__main__':
    test()
