from langdetect import detect


def detectLang(text):
    return 'none'
    # TODO: this library doesn't detect properly. need to replace with better library
    rval = detect(text)
    return rval
